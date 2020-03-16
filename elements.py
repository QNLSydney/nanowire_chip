"""
Draw common elements for a nanowire design
"""
import math
import itertools

import ezdxf
from ezdxf.math import Vector, Matrix44, ConstructionBox

import render_text

def round_vect(vector, precision=3):
    """
    Round a vector to the specified precision.
    """
    return Vector(*(round(x, precision) for x in vector))

def gen_rotate_matrix(angle=90, origin=None):
    """
    Generate a rotation matrix around a point given by origin.
    """
    if origin is None:
        return Matrix44.z_rotate(angle/180*math.pi)
    origin = Vector(origin)

    return (Matrix44.translate(*(-origin))*
            Matrix44.z_rotate(angle/180*math.pi)*
            Matrix44.translate(*origin))

def arrow(dxf_doc, name="arrow", height=150,
          arm_width=30, head_width=100, head_height=60):
    """
    Create an arrow with the name given. The total height of the arrow is
    given by height, and the size of the head is given by head_height. The length
    of just the arm is therefore height-head_height.
    The width of the arm and the bottom of the head are given by arm_width and head_width
    respectively.
    """
    arrow_block = dxf_doc.blocks.new(name)

    # Check the geometry is sensible
    if head_width < arm_width:
        raise ValueError(f"Head ({head_width}) must be wider than the "
                         f"arm ({arm_width}).")
    if head_height > height:
        raise ValueError(f"Head height ({head_height}) must be less than the "
                         f"total height ({height}).")

    # We define the origin of the arrow at the bottom left, as is the case for
    # the elionix mark. The center bottom is here for convenience.
    center_bot = Vector(head_width/2, 0, 0)

    # Start defining the polyline
    cpos = center_bot
    pline = arrow_block.add_polyline2d([cpos])
    cpos = cpos + Vector(arm_width/2, 0, 0)
    pline.append_vertex(cpos)
    cpos = cpos + Vector(0, height-head_height, 0)
    pline.append_vertex(cpos)
    cpos = cpos + Vector((head_width-arm_width)/2, 0, 0)
    pline.append_vertex(cpos)
    cpos = cpos + Vector(-head_width/2, head_height, 0)
    pline.append_vertex(cpos)
    cpos = cpos + Vector(-head_width/2, -head_height, 0)
    pline.append_vertex(cpos)
    cpos = cpos + Vector((head_width-arm_width)/2, 0, 0)
    pline.append_vertex(cpos)
    cpos = cpos + Vector(0, -height+head_height, 0)
    pline.append_vertex(cpos)
    pline.m_close()

    # Return the completed arrow
    return arrow_block

def elionix_mark(dxf_doc, name="AM_elionix",
                 cross_dim=150, center_dim=15,
                 arm_width=10, center_arm_width=1,
                 orientation_square_dim=1.5):
    """
    Create an elionix alignment marker (cross) block. Default dimensions are as given.
    The block is oriented such that the origin is at the bottom left of the cross.

    All dimensions are in um.
    Args:
        layer: The layer on which the block will be created.
        cross_dim: The total square dimension of the cross.
        center_dim: The dimension of the center region with small squares.
        arm_width: The width of the wide arms.
        center_arm_width: The width of the center arm segments.
        orientation_square_dim: The dimensions (square) of the little alignment squares.
    """
    elionix_block = dxf_doc.blocks.new(name=name)

    # Define a rotation around the center
    center = Vector((cross_dim/2, cross_dim/2, 0))
    center_rot = gen_rotate_matrix(origin=center)

    # Calculate relevant numbers for the wide arms and draw them
    bot_left = Vector(cross_dim/2 - arm_width/2, 0, 0)
    top_right = Vector(cross_dim/2 + arm_width/2, cross_dim/2 - center_dim/2, 0)
    arm_rect = (bot_left, top_right)
    for _ in range(4):
        box = ConstructionBox.from_points(*arm_rect)
        elionix_block.add_polyline2d((round_vect(vect) for vect in box)).m_close()
        arm_rect = center_rot.transform_vectors(arm_rect)

    # Draw small arms
    p_1 = center - Vector(center_dim/2, center_arm_width/2, 0)
    p_2 = center - Vector(center_arm_width/2, center_arm_width/2, 0)
    p_3 = center - Vector(center_arm_width/2, center_dim/2, 0)
    cross_points = (p_1, p_2, p_3)
    poly = elionix_block.add_polyline2d([])
    for _ in range(4):
        poly.append_vertices((round_vect(vect) for vect in cross_points))
        cross_points = center_rot.transform_vectors(cross_points)
    poly.m_close()

    # Draw orientation blocks
    bl_center = center - Vector(center_dim/4, center_dim/4, 0)
    tl_box = ConstructionBox.from_points(bl_center, bl_center +
                                         Vector(-orientation_square_dim, orientation_square_dim))
    br_box = ConstructionBox.from_points(bl_center, bl_center +
                                         Vector(orientation_square_dim, -orientation_square_dim))
    elionix_block.add_polyline2d(tl_box).m_close()
    elionix_block.add_polyline2d(br_box).m_close()

    return elionix_block

def elionix_4block(dxf_doc, em_mark, name="AM_elionix_4", block_size=400):
    """
    Create a set of 4 elionix marks, rotated around the center.

    Args:
        doc: The working dxf document
        elionix_mark: The block reference of a single marker.
        block_size: The total (square) size of the alignment block.
    """
    elionix_block = dxf_doc.blocks.new(name=name)

    # Calculate relevant coordinates
    center = Vector(block_size/2, block_size/2, 0)
    center_br = center/2
    center_rot = gen_rotate_matrix(origin=center)

    # Calculate alignment marker size and center
    if isinstance(em_mark, str):
        em_mark = doc.blocks[em_mark]
    if isinstance(em_mark, ezdxf.layouts.BlockLayout):
        bbox = ezdxf.math.BoundingBox2d([(0, 0)])
        for item in em_mark:
            bbox.extend(item.points())
        em_mark_size = bbox.extmax - bbox.extmin
        em_mark_center = bbox.extmin + em_mark_size/2
    else:
        raise TypeError("em_mark must be a dxf Block, or the name of a Block "
                        "defined in the document.")

    # Place markers
    mark_pos = center_br - em_mark_center
    for i in range(4):
        elionix_block.add_blockref(em_mark.dxf.name, mark_pos, dxfattribs={
            'rotation': 90*i,
        })
        mark_pos = round_vect(center_rot.transform(mark_pos))

    return elionix_block

def die_marker(dxf_doc, name="die_marker", arm_thickness=100, arm_length=500):
    """
    Draw a marker for the corner of a die.
    """
    die_block = dxf_doc.blocks.new(name)

    if arm_thickness > arm_length:
        raise ValueError(f"Arm thickness is greater than arm length "
                         f"({arm_thickness} > {arm_length}).")

    # Draw the marker
    cpos = Vector(0, 0, 0)
    pline = die_block.add_polyline2d([cpos])
    cpos = cpos + Vector(arm_length, 0, 0)
    pline.append_vertex(cpos)
    cpos = cpos + Vector(0, arm_thickness, 0)
    pline.append_vertex(cpos)
    cpos = cpos - Vector(arm_length - arm_thickness, 0, 0)
    pline.append_vertex(cpos)
    cpos = cpos + Vector(0, arm_length - arm_thickness, 0)
    pline.append_vertex(cpos)
    cpos = cpos - Vector(arm_thickness, 0, 0)
    pline.append_vertex(cpos)
    pline.m_close()

    # Return the completed marker
    return die_block

def wire_section(dxf_doc, fid=None, sec_size=200, square_dim=5,
                 supp_dist=100, supp_width=1, supp_size=3, sn_size=10):
    """
    Generate a block where nanowires can be placed.
    ID should be a single letter identifier for the block.
    """
    N_RECT = 5
    if fid is None:
        fid = "a"
    name = f"field_{fid}"
    wire_block = dxf_doc.blocks.new(name)

    # Generate rectangles at each corner, starting at the bottom
    center = Vector(sec_size/2, sec_size/2, 0)
    center_rot = gen_rotate_matrix(origin=center)


    rects = []
    bc = Vector(0, 0, 0)
    tc = Vector(square_dim, square_dim, 0)
    offset = Vector(square_dim, square_dim, 0)
    for _ in range(N_RECT):
        cr = ConstructionBox.from_points(bc, tc)
        rects.append([Vector(r) for r in cr])
        bc = tc
        tc = tc + offset

    # Create an offset rectangle for orientation
    tc = bc + Vector(square_dim, -square_dim, 0)
    bc = tc - offset
    orient = [Vector(r) for r in ConstructionBox.from_points(bc, tc)]

    for j in range(4):
        # Add the rectangles at each corner
        for i, rect in enumerate(rects):
            wire_block.add_polyline2d(
                (round_vect(vect) for vect in rect)).m_close()
            rects[i] = list(center_rot.transform_vectors(rect))

        # And the orientation rectangle
        c_orient = gen_rotate_matrix(angle=-90*(j+1), origin=center).\
                        transform_vectors(orient)
        wire_block.add_polyline2d(
            (round_vect(vect) for vect in c_orient)).m_close()
        orient = [vect - offset for vect in orient]

    # Add in supplementary markers
    n_supp = sec_size//supp_dist
    skip = ((0, 0), (n_supp, 0), (0, n_supp), (n_supp, n_supp))
    for i, j in itertools.product(range(n_supp+1), repeat=2):
        if (i, j) in skip:
            continue
        center = Vector(supp_dist*i, supp_dist*j, 0)
        center_rot = gen_rotate_matrix(origin=center)
        p1 = center - Vector(supp_width/2, supp_size/2, 0)
        p2 = p1 + Vector(0, supp_size/2 - supp_width/2, 0)
        p3 = p2 - Vector(supp_size/2 - supp_width/2, 0, 0)
        corner = [p3, p2, p1]

        cross_pline = wire_block.add_polyline2d([])
        for _ in range(4):
            cross_pline.append_vertices((round_vect(vect) for vect in corner))
            corner = center_rot.transform_vectors(corner)
        cross_pline.m_close()

    # Finally, add in the serial marker
    if len(fid) == 1:
        sn_block = render_text.get_glyph(dxf_doc, fid)[0]
    else:
        sn_block = render_text.render_to_block(dxf_doc, fid, name=f"{name}_sn",
                                               height=1)
    sn_pos = Vector(sec_size+5, 0, 0)

    wire_block.add_blockref(sn_block.name, sn_pos, dxfattribs={
        'xscale': sn_size,
        'yscale': sn_size
    })

    return wire_block

def draw_wafer(dxf_doc, diameter=150_000, flat_size=57_500):
    # First we need to calculate the properties of the chord
    chord_angle = math.degrees(2*math.asin(flat_size/diameter))
    center = Vector(diameter/2, diameter/2, 0)

    # Then, calculate the start and stop angles for an arc
    start_angle = 270 + chord_angle/2
    end_angle = 270 - chord_angle/2

    # And the vectors at each side
    start_vect = Vector(diameter, diameter/2, 0)
    end_vect = gen_rotate_matrix(end_angle, origin=center).transform(start_vect)
    start_vect = gen_rotate_matrix(start_angle, origin=center).transform(start_vect)

    wafer_block = dxf_doc.blocks.new("wafer_block")
    wafer_block.add_arc(center, diameter/2, start_angle, end_angle)
    wafer_block.add_line(start_vect, end_vect)
    return wafer_block


if __name__ == "__main__":
    doc = ezdxf.new()
    mark = elionix_mark(doc)
    elionix_4block(doc, mark)
    render_text.render_to_block(doc, "NW200311_0001")
    arrow(doc, name="orientation_arrow")
    die_marker(doc, name="die_marker")
    wire_section(doc, "a")
    with open("test.dxf", "w") as f:
        doc.write(f)
