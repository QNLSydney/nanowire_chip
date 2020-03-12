"""
Module to render text into a DXF from an OTF or a TTF file.
"""

import functools

import numpy as np
from freetype import Face, FT_LOAD_FLAGS

from ezdxf.math import Vector

def repeat_n(iterable, n):
    for i in iterable:
        for _ in range(n):
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

def get_glyph(doc, letter):
    """
    Get a block reference to the given letter
    """
    if not isinstance(letter, str) and len(letter) == 1:
        raise TypeError(f"Letter must be a string of length 1. Got: ({letter}).")

    if getattr(get_glyph, "cache", None) is None or get_glyph.doc is not doc:
        get_glyph.cache = {}
        get_glyph.doc = doc

    if letter in get_glyph.cache:
        return get_glyph.cache[letter]

    name = f"*char_0x{ord(letter):02x}"
    block = doc.blocks.new(name)

    # Load control points from font file
    font = get_font()
    font.load_char(letter, FT_LOAD_FLAGS['FT_LOAD_NO_BITMAP'])
    glyph = font.glyph
    outline = glyph.outline
    points = np.array(outline.points, dtype=float)/font.height
    tags = outline.tags

    # Add splines
    start, end = 0, -1
    for contour in outline.contours:
        start = end + 1
        end = contour

        # Define the font in terms of a cubic spline
        cpoint = start
        spline_points = [Vector(*points[cpoint])]
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
                    # Straight segment
                    for i in range(1, 4):
                        line_point = ((3-i)*points[cpoint] + (i)*npoint)/3
                        spline_points.append(Vector(*line_point))
                    cpoint += 1
                elif ntag & 2:
                    # We are at a cubic bezier curve point
                    if cpoint+3 <= end:
                        spline_points.extend(Vector(*p) for p in points[cpoint+1:cpoint+4])
                    elif cpoint+2 <= end:
                        spline_points.extend(Vector(*p) for p in points[cpoint+1:cpoint+3])
                        spline_points.append(Vector(*points[start]))
                    else:
                        raise ValueError("Missing bezier control points. We require at least"
                                         " two control points to get a cubic curve.")
                    cpoint += 3
                else:
                    # Otherwise we're at a quadratic bezier curve point
                    # Convert the point to a cubic curve point
                    if cpoint + 2 > end:
                        cpoint_2 = start
                        end_tag = tags[start]
                    else:
                        cpoint_2 = cpoint + 2
                        end_tag = tags[cpoint_2]
                    p0 = Vector(*points[cpoint])
                    p1 = Vector(*points[cpoint+1])
                    p2 = Vector(*points[cpoint_2])

                    # Check if we are at a sequential control point. In that case,
                    # p2 is actually the midpoint of p1 and p2.
                    if end_tag & 1 == 0:
                        p2 = (p1 + p2)/2
                    spline_points.extend(_quadratic_to_qubic(p0, p1, p2))
                    cpoint += 2
            else:
                # We are looking at a control point
                if not tags[cpoint] & 2:
                    # We are at a quadratic sequential control point.
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
                        spline_points = [p0]
                    else:
                        # The first control point is at the midpoint of this control point and the
                        # previous control point
                        p0 = Vector(*points[cpoint-1])
                        p1 = Vector(*points[cpoint])
                        p2 = Vector(*points[cpoint_1])
                        p0 = (p0 + p1)/2

                    # Check if we're at the end of the segment
                    if cpoint == end:
                        cpoint_1 = start
                        end_tag = tags[start]
                    else:
                        cpoint_1 = cpoint + 1
                        end_tag = tags[cpoint_1]

                    # Check if we are at a sequential control point again
                    if end_tag & 1 == 0:
                        p2 = (p1 + p2)/2

                    # And add the segment
                    spline_points.extend(_quadratic_to_qubic(p0, p1, p2))
                    cpoint += 1
                else:
                    raise ValueError("Sequential control points not valid for cubic splines.")
        # Finished generating the spline points. Next,generate a sequence of knots
        # that groups points into sequences of cubic splines.
        knots = [0.0]
        knots.extend(repeat_n(range((len(spline_points)+3)//3), 3))
        knots.append(knots[-1])
        knots = [k/knots[-1] for k in knots]

        block.add_open_spline(spline_points, knots=knots, degree=3)

    # Cache the return value and return it
    get_glyph.cache[letter] = (block, glyph.advance.x/font.height)
    return get_glyph.cache[letter]

def render_to_block(doc, text="", name=None, height=10):
    """
    Render some text to a block.
    """
    if not isinstance(text, str):
        raise TypeError("Text must be a string.")

    if name is None:
        block = doc.blocks.new("text_block")
        name = block.name
    else:
        block = doc.blocks.new(name)

    cpos = Vector(0, 0)
    for letter in text:
        letter_block, advance_x = get_glyph(doc, letter)
        block.add_blockref(letter_block.name, cpos)
        cpos = cpos + Vector(advance_x, 0)
