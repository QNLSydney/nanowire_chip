"""
Draw common elements for a nanowire design
"""
import math
import itertools

import gdspy
from mathutils import Vector, Matrix

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
        return Matrix.Rotation(angle/180*math.pi, 4, "Z")
    origin = Vector(origin)

    return (Matrix.Translation(origin)@
            Matrix.Rotation(angle/180*math.pi, 4, "Z")@
            Matrix.Translation(-origin))

def make_polyline(points, layer=0, datatype=0):
    """
    Construct a polyline from a list of Vectors
    """
    points = [poly.xy for poly in points]
    return gdspy.Polygon(points, layer, datatype)

def arrow(pos, height=150, arm_width=30, head_width=100, head_height=60, layer=0):
    """
    Create an arrow with the name given. The total height of the arrow is
    given by height, and the size of the head is given by head_height. The length
    of just the arm is therefore height-head_height.
    The width of the arm and the bottom of the head are given by arm_width and head_width
    respectively.
    """
    # Check the geometry is sensible
    if head_width < arm_width:
        raise ValueError(f"Head ({head_width}) must be wider than the "
                         f"arm ({arm_width}).")
    if head_height > height:
        raise ValueError(f"Head height ({head_height}) must be less than the "
                         f"total height ({height}).")

    # We define the origin of the arrow at the bottom left, as is the case for
    # the elionix mark. The center bottom is here for convenience.
    points = []
    center_bot = pos + Vector((head_width/2, 0, 0))

    # Start defining the polyline
    cpos = center_bot
    points.append(cpos)
    cpos = cpos + Vector((arm_width/2, 0, 0))
    points.append(cpos)
    cpos = cpos + Vector((0, height-head_height, 0))
    points.append(cpos)
    cpos = cpos + Vector(((head_width-arm_width)/2, 0, 0))
    points.append(cpos)
    cpos = cpos + Vector((-head_width/2, head_height, 0))
    points.append(cpos)
    cpos = cpos + Vector((-head_width/2, -head_height, 0))
    points.append(cpos)
    cpos = cpos + Vector(((head_width-arm_width)/2, 0, 0))
    points.append(cpos)
    cpos = cpos + Vector((0, -height+head_height, 0))
    points.append(cpos)

    poly = make_polyline(points, layer=layer)

    # Return the completed arrow
    return poly

def cross(pos=None, size=10, arm_width=2, layer=0):
    """
    Create a cross with a given size and arm width. The cross is placed such that the bottom
    left corner of the bounding box is at pos.

    If position is none, the cross is placed at the origin.
    """
    if pos is None:
        pos = Vector((0, 0, 0))
    # Create the points that define one corner of the cross
    p1 = pos - Vector((size/2, arm_width/2, 0))
    p2 = pos - Vector((arm_width/2, arm_width/2, 0))
    p3 = pos - Vector((arm_width/2, size/2, 0))

    # Define a rotation around the center of the cross
    center_rot = gen_rotate_matrix(origin=pos)

    # Construct the full cross
    cross_points = [p1, p2, p3]
    points = []
    for _ in range(4):
        points.extend(cross_points)
        cross_points = [center_rot@vect for vect in cross_points]
    return make_polyline(points, layer=layer)

def elionix_mark(lib, name="AM_elionix",
                 cross_dim=150, center_dim=15,
                 arm_width=10, center_arm_width=1,
                 orientation_square_dim=1.5,
                 layer=1):
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
    elionix_block = lib.new_cell(name)

    # Define a rotation around the center
    center = Vector((cross_dim/2, cross_dim/2, 0))
    center_rot = gen_rotate_matrix(origin=center)

    # Calculate relevant numbers for the wide arms and draw them
    bot_left = Vector((cross_dim/2 - arm_width/2, 0, 0))
    top_right = Vector((cross_dim/2 + arm_width/2, cross_dim/2 - center_dim/2, 0))
    for _ in range(4):
        elionix_block.add(gdspy.Rectangle(bot_left.xy, top_right.xy, layer=layer))
        bot_left = center_rot@bot_left
        top_right = center_rot@top_right

    # Draw small arms
    elionix_block.add(cross(center, center_dim, center_arm_width, layer=layer))

    # Draw orientation blocks
    bl_center = center - Vector((center_dim/4, center_dim/4, 0))
    tl = bl_center + Vector((-orientation_square_dim, orientation_square_dim, 0))
    br = bl_center + Vector((orientation_square_dim, -orientation_square_dim, 0))
    elionix_block.add(gdspy.Rectangle(bl_center.xy, tl.xy, layer=layer))
    elionix_block.add(gdspy.Rectangle(bl_center.xy, br.xy, layer=layer))

    return elionix_block

def elionix_4block(lib, em_mark, name="AM_elionix_4", block_size=400):
    """
    Create a set of 4 elionix marks, rotated around the center.

    Args:
        doc: The working dxf document
        elionix_mark: The block reference of a single marker.
        block_size: The total (square) size of the alignment block.
    """
    elionix_block = lib.new_cell(name)

    # Calculate relevant coordinates
    center = Vector((block_size/2, block_size/2, 0))
    center_br = center/2
    center_rot = gen_rotate_matrix(origin=center)

    # Calculate alignment marker size and center
    if isinstance(em_mark, str):
        em_mark = lib.cells[em_mark]
    if isinstance(em_mark, gdspy.Cell):
        bbox = em_mark.get_bounding_box()
        em_mark_size = Vector(bbox[1] - bbox[0]).to_3d()
        em_mark_center = Vector(bbox[0]).to_3d() + em_mark_size/2
    else:
        raise TypeError("em_mark must be a dxf Block, or the name of a Block "
                        "defined in the document.")

    # Add construction marks
    for i, j in itertools.product(range(2), repeat=2):
        bl = Vector((i*block_size/2, j*block_size/2, 0))
        tr = Vector(((i+1)*block_size/2, (j+1)*block_size/2, 0))
        elionix_block.add(gdspy.Rectangle(bl, tr, layer=0))

    # Place markers
    mark_pos = center_br - em_mark_center
    for i in range(4):
        elionix_block.add(gdspy.CellReference(em_mark, mark_pos.xy, rotation=90*i))
        mark_pos = center_rot@mark_pos

    return elionix_block

def die_marker(lib, name="die_marker", arm_thickness=100, arm_length=500, layer=1):
    """
    Draw a marker for the corner of a die.
    """
    die_block = lib.new_cell(name)

    if arm_thickness > arm_length:
        raise ValueError(f"Arm thickness is greater than arm length "
                         f"({arm_thickness} > {arm_length}).")

    # Draw the marker
    points = []
    cpos = Vector((0, 0, 0))
    points.append(cpos)
    cpos = cpos + Vector((arm_length, 0, 0))
    points.append(cpos)
    cpos = cpos + Vector((0, arm_thickness, 0))
    points.append(cpos)
    cpos = cpos - Vector((arm_length - arm_thickness, 0, 0))
    points.append(cpos)
    cpos = cpos + Vector((0, arm_length - arm_thickness, 0))
    points.append(cpos)
    cpos = cpos - Vector((arm_thickness, 0, 0))
    points.append(cpos)
    die_block.add(make_polyline(points, layer=layer))

    # Return the completed marker
    return die_block

def wire_section(lib, fid=None, sec_size=200, square_dim=5,
                 supp_dist=100, supp_width=1, supp_size=3, sn_size=10,
                 layer=1):
    """
    Generate a block where nanowires can be placed.
    ID should be a single letter identifier for the block.
    """
    N_RECT = 5
    if fid is None:
        fid = "a"
    name = f"field_{fid}"
    wire_block = lib.new_cell(name)

    # Generate rectangles at each corner, starting at the bottom
    center = Vector((sec_size/2, sec_size/2, 0))
    center_rot = gen_rotate_matrix(origin=center)

    rects = lib.new_cell(f"{name}_align_rects")
    bc = Vector((0, 0, 0)) - center
    tc = Vector((square_dim, square_dim, 0)) - center
    offset = Vector((square_dim, square_dim, 0))
    for _ in range(N_RECT):
        rects.add(gdspy.Rectangle(bc.xy, tc.xy, layer=layer))
        bc = tc
        tc = tc + offset

    # Create an offset rectangle for orientation
    tc = bc + Vector((square_dim, -square_dim, 0)) + center
    bc = tc - offset
    for j in range(4):
        # Add the rectangles at each corner
        wire_block.add(gdspy.CellReference(rects, center.xy, rotation=j*90))
        # And the orientation rectangle
        wire_block.add(gdspy.Rectangle(bc.xy, tc.xy, layer=layer))
        bc = center_rot@(bc - offset)
        tc = center_rot@(tc - offset)
        offset = gen_rotate_matrix()@offset

    # Add in supplementary markers
    n_supp = sec_size//supp_dist
    skip = ((0, 0), (n_supp, 0), (0, n_supp), (n_supp, n_supp))
    for i, j in itertools.product(range(n_supp+1), repeat=2):
        if (i, j) in skip:
            continue
        center = Vector((supp_dist*i, supp_dist*j, 0))
        wire_block.add(cross(center, supp_size, supp_width, layer=layer))

    # Finally, add in the serial marker
    if len(fid) == 1:
        sn_block = render_text.get_glyph(lib, fid, layer=layer)[0]
    else:
        sn_block = render_text.render_to_block(lib, fid, name=f"{name}_sn",
                                               height=1, layer=layer)
    sn_pos = Vector((sec_size+5, 0, 0))
    wire_block.add(gdspy.CellReference(sn_block, sn_pos.xy, magnification=sn_size))

    return wire_block

def draw_wafer(lib, diameter=150_000, flat_size=57_500, layer=0):
    # First we need to calculate the properties of the chord
    chord_angle = 2*math.asin(flat_size/diameter)
    center = Vector((diameter/2, diameter/2, 0))

    # Then, calculate the start and stop angles for an arc
    initial_angle = -chord_angle/2 + 3*math.pi/2
    final_angle = chord_angle/2 - math.pi/2

    # Find the positions of the start and the end
    start_vect = Vector((diameter, diameter/2, 0))
    start_vect = gen_rotate_matrix(math.degrees(initial_angle), center)@start_vect

    curve = gdspy.Curve(*start_vect.xy, tolerance=10)
    curve.arc(diameter/2, initial_angle, final_angle)
    return gdspy.Polygon(curve.get_points(), layer=layer)


if __name__ == "__main__":
    doc = gdspy.GdsLibrary()
    mark = elionix_mark(doc)
    elionix_4block(doc, mark)
    render_text.render_to_block(doc, "NW200311_0001")
    arrow_cell = gdspy.Cell("arrow")
    arrow_cell.add(arrow(Vector((0, 0, 0))))
    doc.add(arrow_cell)
    die_marker(doc, name="die_marker")
    wire_section(doc, "a")
    draw_wafer(doc)
    with open("test.gds", "wb") as f:
        doc.write_gds(f)
