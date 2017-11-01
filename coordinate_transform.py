import dxfwrite
import numpy
import math
from dxfwrite import DXFEngine as dxf

# Create a rotation array to rotate by the angle theta
def rot_mat(theta):
    c, s = numpy.cos(theta), numpy.sin(theta)
    return numpy.array(((c, -s), (s, c)))

# The following code assumes that the origin is in the bottom left.
# In photoshop this will mean entering -y for the coordinates.
# The first argument is the alignment marker coords (bl, br, tl, tr)
# Following this, pass in the two coordinates of the nanowire.
def find_nw(marker_coords, nw_coords, die_dims=(300, 300)):
    # Check that our arrays are numpy arrays
    if not isinstance(marker_coords, numpy.ndarray):
        marker_coords = numpy.array(marker_coords)
    if not isinstance(nw_coords, numpy.ndarray):
        nw_coords = numpy.array(nw_coords)

    # Check that we have the right number of coordinates
    if marker_coords.shape != (4,2):
        raise ValueError("marker_coords should be a set of four (x, y) coordinates")
    if nw_coords.shape != (2,2):
        raise ValueError("nw_coords should be a set of two (x, y) coordinates")

    # Change the origin to the bottom left marker
    nw_coords -= marker_coords[0]
    marker_coords -= marker_coords[0]

    # Transpose coordinate system for easier multiplication
    marker_coords = marker_coords.transpose()
    nw_coords = nw_coords.transpose()

    # Rotate the diagonal
    theta = math.pi/4 - math.atan2(marker_coords[1,3], marker_coords[0,3])
    rot_m = rot_mat(theta)
    marker_coords = rot_m @ marker_coords
    nw_coords = rot_m @ nw_coords

    #calculating the x-deskew transform
    x_skew = marker_coords[0,2]/marker_coords[1,2]
    x_skew_matrix = numpy.array([[1, -x_skew], [0, 1]])

    #run the coordinate transform for x first
    marker_coords = x_skew_matrix @ marker_coords
    nw_coords = x_skew_matrix @ nw_coords

    # And the y-deskew transform
    y_skew = marker_coords[1,1]/marker_coords[0,1]
    y_skew_matrix = numpy.array([[1, 0], [-y_skew, 1]])

    # And run the coordinate transforms
    marker_coords = y_skew_matrix @ marker_coords
    nw_coords = y_skew_matrix @ nw_coords

    # Stretch the image such that we match the dimensions of the grid
    stretch_matrix = numpy.diag(numpy.divide(die_dims, ((marker_coords[0, 1], marker_coords[1, 2]))))
    marker_coords = stretch_matrix @ marker_coords
    nw_coords = stretch_matrix @ nw_coords

    # Finally, we correct for the distortion of the top corner to make the image square
    # As this is not a linear transformation, we cannot simply use matrix operations here.
    distort_corr = (numpy.divide(marker_coords[:,3], die_dims) - 1)/numpy.multiply.reduce(marker_coords[:,3])
    distort_corr_mc = numpy.tensordot(distort_corr, numpy.multiply.reduce(marker_coords), axes=0) + 1
    distort_corr_nw = numpy.tensordot(distort_corr, numpy.multiply.reduce(nw_coords), axes=0) + 1
    marker_coords = marker_coords / distort_corr_mc
    nw_coords = nw_coords / distort_corr_nw

    # And transpose back
    marker_coords = marker_coords.transpose()
    nw_coords = nw_coords.transpose()

    return (marker_coords, nw_coords)

if __name__ == "__main__":
    # The dimensions of the die in microns
    die_dims = (300, 300)

    #note that you have to make all the y coordinates negative (even though they will not be in photoshop)
    #this is because photoshop calls the top left corner (0,0) and then decreasing in the y direction actually becomes
    #more positive in photoshop
    coord_botleft = (196,-952)
    coord_botright = (1124,-974)
    coord_topleft = (219,-21)
    coord_topright = (1148,-46)
    nw_1 = (737,-540)
    nw_2 = (763,-522)

    (marker, nw) = find_nw((coord_botleft, coord_botright, coord_topleft, coord_topright),
            (nw_1, nw_2), die_dims=die_dims)
    print("Marker Coordinates: ")
    print(marker)
    print("NW Coordinates")
    print(nw)

