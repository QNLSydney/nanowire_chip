""" Generate ids to be placed into a beamer grid file """
import sys
import argparse

# Beamer format for serial numbers
TEXT_VAL = """TEXT_VALUES
TEXT_NAME = {id}_{sn:04d}
TEXT_COMMENT = 
TEXT_ARRAYID = 1
TEXT_ARRAYPOS = ({x}%2C%20{y})
TEXT_OFFSETX = 0.000000
TEXT_OFFSETY = -1800.000000
TEXT_SIZE = 125.000000
TEXT_ROTATION = 0%20degree
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", type=int, default=11, help="Number of chips in X-dimension")
    parser.add_argument("-y", type=int, default=11, help="Number of chips in Y-dimension")
    parser.add_argument("-s", "--size", type=float, default=3.9, help="Size of the wafer in inches")
    parser.add_argument("-t", "--template", type=str, default="Layout_Template.ftxt.templ", 
                        help="Template to use to generate beamer output")
    parser.add_argument("ID", type=str, help="ID string for the wafer")
    parser.add_argument("INPUT", type=str, help="Name of the input dxf file")
    parser.add_argument("OUTPUT", type=str, help="Output beamer file name")
    args = parser.parse_args()

    # Read in the template beamer file
    with open(args.template, "r") as f:
        templ = f.read()

    # Generate list of serial numbers
    output = []
    for i in range(args.x):
        for j in range(args.y):
            output.append(TEXT_VAL.format(x=i+1, y=j+1, id=args.ID, sn=1 + j + i*args.x))

    # Write the output beamer file
    with open(args.OUTPUT, "w") as f:
        ids = "\n".join(output)
        f.write(templ.format(X=args.x, Y=args.y, dxf=args.INPUT,
                             substr_size=args.size, ids=ids))

    print("Written output beamer file to {}.".format(args.OUTPUT))
