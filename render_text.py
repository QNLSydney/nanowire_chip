"""
Module to render text into a DXF from an OTF or a TTF file.
"""

import functools

import numpy as np
from freetype import Face, FT_LOAD_FLAGS

import gdspy
from mathutils import Vector

def repeat_n(iterable, n_iter):
    """
    Repeat each element of the iterable n times.
    """
    for i in iterable:
        for _ in range(n_iter):
            yield i

def _quadratic_to_qubic(p0, p1, p2):
    """
    Convert a quadratic bezier curve (with control point p1) into a cubic
    bezier curve.

    Note the start point is NOT returned.
    """
    # We are at a quadratic bezier curve point. We need to convert this into a
    # cubic curve for this implementation
    cp1 = p0 + 2/3*(p1-p0)
    cp2 = p2 - 2/3*(p2-p1)

    return (cp1, cp2, p2)

@functools.lru_cache(maxsize=2)
def get_font(font="SourceCodePro-Bold.otf"):
    """
    Get the font renderer from freetype
    """
    font_renderer = Face(font)
    font_renderer.set_char_size(32*64) # 32pt size
    return font_renderer

def get_glyph(lib, letter, layer=0):
    """
    Get a block reference to the given letter
    """
    if not isinstance(letter, str) and len(letter) == 1:
        raise TypeError(f"Letter must be a string of length 1. Got: ({letter}).")

    if getattr(get_glyph, "cache", None) is None or get_glyph.doc is not lib:
        get_glyph.cache = {}
        get_glyph.doc = lib

    if (letter, layer) in get_glyph.cache:
        return get_glyph.cache[(letter, layer)]

    name = f"char_{layer}_0x{ord(letter):02x}"
    block = lib.new_cell(name)

    # Load control points from font file
    font = get_font()
    font.load_char(letter, FT_LOAD_FLAGS['FT_LOAD_NO_BITMAP'])
    glyph = font.glyph
    outline = glyph.outline
    points = np.array(outline.points, dtype=float)/font.height
    tags = outline.tags

    # Add polylines
    start, end = 0, -1
    polylines = []
    for contour in outline.contours:
        start = end + 1
        end = contour

        # Build up the letter as a curve
        cpoint = start
        curve = gdspy.Curve(*points[cpoint], tolerance=0.001)
        while cpoint <= end:
            # Figure out what sort of point we are looking at
            if tags[cpoint] & 1:
                # We are at an on-curve control point. The next point may be
                # another on-curve point, in which case we create a straight
                # line interpolation, or it may be a quadratic or cubic
                # bezier curve. But first we check if we are at the end of the array
                if cpoint == end:
                    ntag = tags[start]
                    npoint = points[start]
                else:
                    ntag = tags[cpoint+1]
                    npoint = points[cpoint+1]

                # Then add the control points
                if ntag & 1:
                    curve.L(*npoint)
                    cpoint += 1
                elif ntag & 2:
                    # We are at a cubic bezier curve point
                    if cpoint+3 <= end:
                        curve.C(*points[cpoint+1:cpoint+4].flatten())
                    elif cpoint+2 <= end:
                        curve.C(*points[cpoint+1:cpoint+3].flatten(), *points[start])
                    else:
                        raise ValueError("Missing bezier control points. We require at least"
                                         " two control points to get a cubic curve.")
                    cpoint += 3
                else:
                    # Otherwise we're at a quadratic bezier curve point
                    if cpoint + 2 > end:
                        cpoint_2 = start
                        end_tag = tags[start]
                    else:
                        cpoint_2 = cpoint + 2
                        end_tag = tags[cpoint_2]
                    p1 = Vector(*points[cpoint+1])
                    p2 = Vector(*points[cpoint_2])

                    # Check if we are at a sequential control point. In that case,
                    # p2 is actually the midpoint of p1 and p2.
                    if end_tag & 1 == 0:
                        p2 = (p1 + p2)/2

                    # Add the curve
                    curve.Q(*p1, *p2)
                    cpoint += 2
            else:
                # We are looking at a control point
                if not tags[cpoint] & 2:
                    # We are at a quadratic sequential control point.
                    # Check if we're at the end of the segment
                    if cpoint == end:
                        cpoint_1 = start
                        end_tag = tags[start]
                    else:
                        cpoint_1 = cpoint + 1
                        end_tag = tags[cpoint_1]

                    # If we are at the beginning, this is a special case,
                    # we need to reset the starting position
                    if cpoint == start:
                        p0 = Vector(*points[end])
                        p1 = Vector(*points[cpoint])
                        p2 = Vector(*points[cpoint_1])
                        if tags[end] & 1 == 0:
                            # If the last point is also a control point, then the end is actually
                            # halfway between here and the last point
                            p0 = (p0 + p1)/2
                        # And reset the starting position of the spline
                        curve = gdspy.Curve(*p0, tolerance=0.001)
                    else:
                        # The first control point is at the midpoint of this control point and the
                        # previous control point
                        p0 = Vector(*points[cpoint-1])
                        p1 = Vector(*points[cpoint])
                        p2 = Vector(*points[cpoint_1])
                        p0 = (p0 + p1)/2

                    # Check if we are at a sequential control point again
                    if end_tag & 1 == 0:
                        p2 = (p1 + p2)/2

                    # And add the segment
                    curve.Q(*p1, *p2)
                    cpoint += 1
                else:
                    raise ValueError("Sequential control points not valid for cubic splines.")
        polylines.append(gdspy.Polygon(curve.get_points(), layer=layer))

    # Construct the letter
    letter_polyline = polylines[0]
    for polyline in polylines[1:]:
        letter_polyline = gdspy.boolean(letter_polyline, polyline, "xor", layer=layer)
    block.add(letter_polyline)

    # Cache the return value and return it
    get_glyph.cache[(letter, layer)] = (block, glyph.advance.x/font.height)
    return get_glyph.cache[(letter, layer)]

def render_to_block(lib, text="", name=None, height=10, layer=0):
    """
    Render some text to a block.
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    if name is None:
        block = lib.new_cell("text_block")
    else:
        block = lib.new_cell(name)

    cpos = Vector((0, 0, 0))
    for letter in text:
        letter_block, advance_x = get_glyph(lib, letter, layer=layer)
        block.add(gdspy.CellReference(letter_block, cpos.xy, magnification=height))
        cpos = cpos + Vector((advance_x*height, 0, 0))

    return block, cpos
