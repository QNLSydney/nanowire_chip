#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011-2015 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
#  - The code is incomplete and over-simplified, as it ignores the 3rd order
#    bezier curve bit and always intepolate between off-curve points.
#    This is only correct for truetype fonts (which only use 2nd order bezier curves).
#  - Also it seems to assume the first point is always on curve; this is
#    unusual but legal.
#
# -----------------------------------------------------------------------------
'''
Show how to access glyph outline description.
'''
from freetype import *

if __name__ == '__main__':
    import numpy
    import matplotlib.pyplot as plt
    from matplotlib.path import Path
    import matplotlib.patches as patches
    plt.ion()

    face = Face('./SourceCodePro-Bold.otf')
    face.set_char_size(32*64*4)
    face.load_char('e')
    slot = face.glyph

    bitmap = face.glyph.bitmap
    width  = face.glyph.bitmap.width
    rows   = face.glyph.bitmap.rows
    pitch  = face.glyph.bitmap.pitch

    data = []
    for i in range(rows):
        data.extend(bitmap.buffer[i*pitch:i*pitch+width])
    Z = numpy.array(data, dtype=numpy.ubyte).reshape(rows, width)

    outline = slot.outline
    points = numpy.array(outline.points, dtype=[('x', float), ('y', float)])
    x, y = points['x'], points['y']

    figure = plt.figure(figsize=(8, 10))
    axis = figure.add_subplot(111)
    #axis.scatter(points['x'], points['y'], alpha=.25)
    start, end = 0, -1

    VERTS, CODES = [], []
    # Iterate over each contour
    for i in range(len(outline.contours)):
        start = end + 1
        end = outline.contours[i]
        points = outline.points[start:end+1]
        points.append(points[0])
        tags   = outline.tags[start:end+1]
        tags.append(tags[0])

        segments = [(Path.MOVETO, [points[0]]), (Path.LINETO, [points[0]])]
        for j, tag in enumerate(tags):
            if j == 0:
                continue
            print(tag)
            if (tag & 1) == 1:
                # Close previous segment
                segments[-1][1].append(points[j])
                # And open a new segment
                segments.append((Path.LINETO, [points[j]]))
            elif (tag & 1) == 0 and (tag & 2) == 0:
                print("Second order")
                # Second order bezier arc
                segments[-1] = (Path.CURVE3, [points[j]])
            elif (tag & 1) == 0 and (tag & 2) == 2:
                print("Third order")
                # Third order bezier arc
                if segments[-1][0] == Path.LINETO:
                    segments[-1] = (Path.CURVE4, [points[j]])
                else:
                    segments[-1][1].append(points[j])

        verts = []
        codes = []
        for segment in segments:
            verts.extend(segment[1])
            for _ in segment[1]:
                codes.append(segment[0])

        VERTS.extend(verts)
        CODES.extend(codes)

    # Draw glyph
    path = Path(VERTS, CODES)
    glyph = patches.PathPatch(path, fill = True, facecolor=(0.8,0.5,0.8), alpha=.25, lw=0)
    glyph_outline = patches.PathPatch(path, fill = False, edgecolor='red', lw=3)

    plt.imshow(Z, extent=[x.min(), x.max(),y.min(), y.max()], origin='upper', cmap = "gray_r")
    plt.xticks(numpy.linspace(x.min(), x.max(), Z.shape[1]+1), ())
    plt.yticks(numpy.linspace(y.min(), y.max(), Z.shape[0]+1), ())
    #plt.grid(color='k', linewidth=1, linestyle='-')
    axis.add_patch(glyph)
    axis.add_patch(glyph_outline)
    axis.set_xlim(x.min(), x.max())
    axis.set_ylim(y.min(), y.max())

    plt.savefig('glyph-vector-2.svg')
    plt.show()
