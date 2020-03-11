"""
Draw common elements for a nanowire design
"""
import math

import ezdxf
from ezdxf.math import Vector, Matrix44, ConstructionBox

import render_text

def round_vect(vector, precision=3):
    """
    Round a vector to the specified precision.
    """
    return Vector(*(round(x, precision) for x in vector))

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
    center_rot = (Matrix44.translate(*(-center))*
                  Matrix44.z_rotate(math.pi/2)*
                  Matrix44.translate(*center))

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
    center_rot = (Matrix44.translate(*(-center))*
                  Matrix44.z_rotate(math.pi/2)*
                  Matrix44.translate(*center))

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

if __name__ == "__main__":
    doc = ezdxf.new()
    mark = elionix_mark(doc)
    elionix_4block(doc, mark)
    render_text.render_to_block(doc, "The quick brown fox jumps over the lazy dog. 1234567890")
    with open("test.dxf", "w") as f:
        doc.write(f)
