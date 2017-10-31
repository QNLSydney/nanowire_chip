import matplotlib.pyplot as plt
import cv2
import numpy
import math

# Create a rotation array to rotate by the angle theta
def rot_mat(theta):
    c, s = numpy.cos(theta), numpy.sin(theta)
    return numpy.array(((c, -s), (s, c)))

def showimage(img, name, points=None):
    plt.imshow(img)
    if points is not None:
        print(points[:,0])
        plt.scatter(points[:,0], points[:,1], s=2, alpha=0.5)
    plt.title(name)
    plt.show()

# The following code assumes that the origin is in the !!top left!!.
# The first argument is the alignment marker coords (tl, tr, bl, br)
# Following this, pass in the two coordinates of the nanowire.
def find_nw(marker_coords, nw_coords, die_dims=(300, 300), img=None, 
            transform_offset=0, transform_scale=1):
    # Check that our arrays are numpy arrays
    if not isinstance(marker_coords, numpy.ndarray):
        marker_coords = numpy.array(marker_coords, dtype=numpy.float32)
    if not isinstance(nw_coords, numpy.ndarray):
        nw_coords = numpy.array(nw_coords, dtype=numpy.float32)

    # Check that we have the right number of coordinates
    if marker_coords.shape != (4,2):
        raise ValueError("marker_coords should be a set of four (x, y) coordinates")
    if nw_coords.shape != (2,2):
        raise ValueError("nw_coords should be a set of two (x, y) coordinates")

    # Check that we've passed in an image
    have_image = False
    if isinstance(img, numpy.ndarray):
        have_image = True
    elif img is not None:
        raise ValueError("img must be an image read in by cv2.imread")

    # Do an openCV Perspective Transform
    # Note, desired coordinates are offset in order to show a border
    desired_coords = numpy.array(((0, 0), (die_dims[0], 0), (0, die_dims[1]), die_dims)) * transform_scale
    desired_coords += transform_offset
    desired_coords = numpy.float32(desired_coords)
    M = cv2.getPerspectiveTransform(marker_coords, desired_coords)

    # And transform the raw coordinates
    marker_coords = cv2.perspectiveTransform(numpy.array([marker_coords]), M)[0]
    nw_coords = cv2.perspectiveTransform(numpy.array([nw_coords]), M)[0]

    # If we have the image, show it
    if have_image:
        size = (numpy.array(die_dims) * transform_scale) + transform_offset
        size = tuple(size)
        dst = cv2.warpPerspective(img, M, size)
        showimage(dst, "result", numpy.concatenate((marker_coords, nw_coords)))
        cv2.imwrite("res.tif", dst)

    # Remove the offset that we've added for visualization purposes
    marker_coords -= 100
    nw_coords -= 100
    # And undo any visualization scaling
    marker_coords /= 2
    nw_coords /= 2

    return (marker_coords, nw_coords)

if __name__ == "__main__":
    # Open the raw image (if available)
    im = cv2.imread("NW170926_05601.tif")
    print(im.shape)
    die_dims = (300, 300)

    #note that you have to make all the y coordinates negative (even though they will not be in photoshop)
    #this is because photoshop calls the top left corner (0,0) and then decreasing in the y direction actually becomes
    #more positive in photoshop
    coord_botleft = (500, 1935)
    coord_botright = (2432, 1956)
    coord_topleft = (540, 19)
    coord_topright = (2473, 40)
    nw_1 = (1677,1647)
    nw_2 = (1688,1709)

    (marker, nw) = find_nw((coord_topleft, coord_topright, coord_botleft, coord_botright),
            (nw_1, nw_2), die_dims=die_dims, img=im, transform_scale=5)

    print("Marker Coordinates: ")
    print(marker)
    print("NW Coordinates")
    print(nw)
    print("NW Coordinates, shifted origin")
    print(numpy.abs(nw - (0, 300)))

