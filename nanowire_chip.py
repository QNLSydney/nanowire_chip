"""
Module to render text into a DXF from an OTF or a TTF file.
"""

import itertools

import gdspy
from mathutils import Vector

import elements
import render_text

def die(lib, die_size, chip_size, die_mark_offset=100, alignment_layer=1):
    """
    Draw a complete die
    """
    die_block = lib.new_cell("die")

    # Generate critical dimensions
    center = Vector((die_size/2, die_size/2, 0))
    center_rot = elements.gen_rotate_matrix(origin=center)
    chip_corner = center - Vector((chip_size/2, chip_size/2, 0))
    die_rect = gdspy.Rectangle((0, 0), (die_size, die_size), layer=0)
    chip_rect = gdspy.Rectangle(chip_corner.xy, (chip_corner + Vector((chip_size, chip_size, 0))).xy, layer=0)
    die_block.add(die_rect)
    die_block.add(chip_rect)

    # Add centerlines
    bc = Vector((die_size/2, 0, 0))
    lc = Vector((0, die_size/2, 0))
    die_block.add(gdspy.Path(0.001, lc).segment(die_size, "+x"))
    die_block.add(gdspy.Path(0.001, bc).segment(die_size, "+y"))

    # Generate the corners
    corner_mark = elements.die_marker(lib, layer=alignment_layer)
    chip_corner_mark = elements.die_marker(lib, name="chip_corner_mark",
                                           arm_thickness=25, arm_length=100, layer=1)
    insert_loc = Vector((die_mark_offset, die_mark_offset, 0))
    chip_insert_loc = chip_corner - insert_loc/2
    for i in range(4):
        die_block.add(gdspy.CellReference(corner_mark, insert_loc.xy, rotation=i*90))
        die_block.add(gdspy.CellReference(chip_corner_mark, chip_insert_loc.xy, rotation=i*90))
        insert_loc = center_rot@insert_loc
        chip_insert_loc = center_rot@chip_insert_loc

    # Add the alignment marks
    em_mark = elements.elionix_mark(lib, layer=alignment_layer)
    em_4block = elements.elionix_4block(lib, em_mark)
    insert_loc = chip_corner + Vector((100, 100, 0))
    for i in range(4):
        die_block.add(gdspy.CellReference(em_4block, insert_loc.xy, rotation=i*90))
        insert_loc = center_rot@insert_loc

    # Add the orientation arrow
    insert_loc = insert_loc + Vector((600, 0, 0))
    orient = elements.arrow(insert_loc, height=400, arm_width=100, head_width=300,
                            head_height=200, layer=alignment_layer)
    die_block.add(orient)

    # Generate wire locations
    sections = ("a", "c", "d", "b")
    offs = Vector((300, 0, 0)) - Vector((-100, 100, 0))
    offs_rot = elements.gen_rotate_matrix(origin=Vector((300/2, 300/2, 0)))
    for i, sec in enumerate(sections):
        print(offs)
        wire_sec = elements.wire_section(lib, sec, sec_size=300, sn_size=20)
        die_block.add(gdspy.CellReference(wire_sec, (center-offs).xy))
        offs = offs_rot@offs

    # Calculate SN location
    sn_loc = chip_corner + Vector((chip_size/2, 100, 0))

    return die_block, sn_loc


if __name__ == "__main__":
    WAFER_SIZE = 150_000
    DIE_SIZE = 7_500
    CHIP_SIZE = 5_000
    SN_FORMAT = "NW200312_HRALOX_{:04d}"
    FILENAME = "NW200312_HRALOX.gds"

    doc = gdspy.GdsLibrary()
    top_level = doc.new_cell("top")

    # Draw a wafer outline
    wafer = elements.draw_wafer(doc, layer=0)
    top_level.add(wafer)

    # Insert dies
    die_block, sn_loc = die(doc, DIE_SIZE, CHIP_SIZE)
    die_vect = Vector((DIE_SIZE, DIE_SIZE, 0))
    wafer_center = Vector((WAFER_SIZE/2, WAFER_SIZE/2, 0))
    x, y = 0, 0
    did = 1
    while y < WAFER_SIZE:
        x = 0
        while x < WAFER_SIZE:
            loc = Vector((x, y, 0))
            # Check that the location is contained in the wafer
            contained = True
            for i, j in itertools.product(range(2), repeat=2):
                vect = loc + Vector((i*DIE_SIZE, j*DIE_SIZE, 0)) - wafer_center
                if vect.magnitude > WAFER_SIZE/2:
                    contained = False
            if not contained:
                x += DIE_SIZE
                continue
            # Add the chip
            top_level.add(gdspy.CellReference(die_block, loc.xy))

            # Generate SN
            sn = SN_FORMAT.format(did)
            sn_block, text_size = render_text.render_to_block(doc, sn, f"sn_{sn}",
                                                              height=150, layer=1)
            top_level.add(gdspy.CellReference(sn_block, (loc + sn_loc - text_size/2).xy))
            did += 1

            x += DIE_SIZE
        y += DIE_SIZE

    with open(FILENAME, "wb") as f:
        doc.write_gds(f)
