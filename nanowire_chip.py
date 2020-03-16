"""
Module to render text into a DXF from an OTF or a TTF file.
"""

import ezdxf
from ezdxf.math import Vector, ConstructionBox

import elements
import render_text

def die(dxf_doc, die_size, chip_size, die_mark_offset=100):
    """
    Draw a complete die
    """
    die_block = dxf_doc.blocks.new("die")
    construction_layer = dxf_doc.layers.get("Construction")
    alignment_layer = dxf_doc.layers.get("Alignment")

    # Generate critical dimensions
    center = Vector(die_size/2, die_size/2, 0)
    center_rot = elements.gen_rotate_matrix(origin=center)
    chip_corner = center - Vector(chip_size/2, chip_size/2, 0)
    die_rect = ConstructionBox(center, die_size, die_size)
    chip_rect = ConstructionBox(center, chip_size, chip_size)
    die_block.add_polyline2d(die_rect, dxfattribs={
        'layer': construction_layer.dxf.name}).m_close()
    die_block.add_polyline2d(chip_rect, dxfattribs={
        'layer': construction_layer.dxf.name}).m_close()

    # Generate the corners
    corner_mark = elements.die_marker(dxf_doc)
    chip_corner_mark = elements.die_marker(dxf_doc, name="chip_corner_mark",
                                           arm_thickness=25, arm_length=100)
    insert_loc = Vector(die_mark_offset, die_mark_offset, 0)
    chip_insert_loc = chip_corner - insert_loc/2
    for i in range(4):
        attribs = {
            'layer': alignment_layer.dxf.name
        }
        blockattribs = {
            'layer': alignment_layer.dxf.name,
            'rotation': i*90
        }
        die_block.add_auto_blockref(corner_mark.name, insert_loc, attribs,
                                    dxfattribs=blockattribs)
        die_block.add_auto_blockref(chip_corner_mark.name, chip_insert_loc, attribs,
                                    dxfattribs=blockattribs)
        insert_loc = elements.round_vect(center_rot.transform(insert_loc))
        chip_insert_loc = elements.round_vect(center_rot.transform(chip_insert_loc))

    # Add the alignment marks
    em_mark = elements.elionix_mark(dxf_doc)
    em_4block = elements.elionix_4block(dxf_doc, em_mark)
    insert_loc = chip_corner + Vector(100, 100)
    for i in range(4):
        attribs = {
            'layer': alignment_layer.dxf.name
        }
        blockattribs = {
            'layer': alignment_layer.dxf.name,
            'rotation': i*90
        }
        die_block.add_auto_blockref(em_4block.name, insert_loc, attribs,
                                    dxfattribs=blockattribs)
        insert_loc = elements.round_vect(center_rot.transform(insert_loc))

    # Add the orientation arrow
    orient = elements.arrow(dxf_doc, name="orient_arrow", height=400, arm_width=100,
                            head_width=300, head_height=200)
    insert_loc = insert_loc + Vector(600, 0, 0)
    attribs = {
        'layer': alignment_layer.dxf.name
    }
    die_block.add_auto_blockref(orient.name, insert_loc, attribs,
                                dxfattribs=attribs)

    # Generate wire locations
    sections = ("a", "c", "d", "b")
    insert_loc = center + Vector(-100, 100, 0)
    offs = Vector(300, 0, 0)
    offs_rot = elements.gen_rotate_matrix(origin=(300/2, 300/2, 0))
    for i, sec in enumerate(sections):
        wire_sec = elements.wire_section(dxf_doc, sec, sec_size=300, sn_size=20)
        die_block.add_auto_blockref(wire_sec.name, insert_loc-offs, attribs,
                                    dxfattribs=attribs)
        insert_loc = elements.round_vect(center_rot.transform(insert_loc))
        offs = elements.round_vect(offs_rot.transform(offs))

    # Calculate SN location
    sn_loc = chip_corner + Vector(chip_size/2, 100)

    return die_block, sn_loc


if __name__ == "__main__":
    WAFER_SIZE = 150_000
    DIE_SIZE = 7_500
    CHIP_SIZE = 5_000
    SN_FORMAT = "NW200312_HRALOX_{:04d}"
    FILENAME = "NW200312_HRALOX.dxf"

    doc = ezdxf.new()
    msp = doc.modelspace()
    construction_layer = doc.layers.new("Construction", dxfattribs={
        'color': 7
    })
    alignment_layer = doc.layers.new("Alignment", dxfattribs={
        'color': 1
    })

    # Draw a wafer outline
    wafer = elements.draw_wafer(doc)
    wafer_center = Vector(WAFER_SIZE/2, WAFER_SIZE/2, 0)
    attribs = {
        'layer': construction_layer.dxf.name
    }
    msp.add_auto_blockref(wafer.name, Vector(0, 0, 0), attribs,
                          dxfattribs=attribs)

    # Insert dies
    die_block, sn_loc = die(doc, DIE_SIZE, CHIP_SIZE)
    die_vect = Vector(DIE_SIZE, DIE_SIZE)
    x, y = 0, 0
    did = 1
    attribs = {
        'layer': alignment_layer.dxf.name
    }
    while y < WAFER_SIZE:
        x = 0
        while x < WAFER_SIZE:
            loc = Vector(x, y, 0)
            # Check that the location is contained in the wafer
            loc_bbox = ConstructionBox.from_points(loc-wafer_center,
                                                   loc+die_vect-wafer_center)
            contained = True
            for vect in loc_bbox:
                vect = Vector(vect)
                if vect.magnitude > WAFER_SIZE/2:
                    contained = False
            if not contained:
                x += DIE_SIZE
                continue

            # Add the chip
            msp.add_blockref(die_block.name, loc)

            # Generate SN
            sn = SN_FORMAT.format(did)
            sn_block, text_size = render_text.render_to_block(doc, sn, f"*{sn}", height=150)
            msp.add_auto_blockref(sn_block.name, loc + sn_loc - text_size/2, attribs,
                                  dxfattribs=attribs)
            did += 1

            x += DIE_SIZE
        y += DIE_SIZE

    with open(FILENAME, "w") as f:
        doc.write(f)
