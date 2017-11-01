import dxfwrite
import os
import sys
import numpy
import random
import math
#import elionix_alignment as eal
from dxfwrite import DXFEngine as dxf


die_width = 300
die_height = 300

#note that you have to make all the y coordinates negative (even though they will not be in photoshop)
#this is because photoshop calls the top left corner (0,0) and then decreasing in the y direction actually becomes
#more positive in photoshop

coord_botleft = (184,-948)
coord_botright = (1113,-978)
coord_topleft = (215,-19)
coord_topright = (1143,-50)
nw_1 = (741,-518)
nw_2 = (742,-487)

#centering on the bottom left corner of the rectangle
new_botleft = (0,0)
new_botright = tuple(numpy.subtract(coord_botright, coord_botleft))
new_topright = tuple(numpy.subtract(coord_topright, coord_botleft))
new_topleft = tuple(numpy.subtract(coord_topleft, coord_botleft))
#transforming the nanowire coordinates as well
new_nw1 = tuple(numpy.subtract(nw_1, coord_botleft))
new_nw2 = tuple(numpy.subtract(nw_2, coord_botleft))

#calculating the x transform
theta_x = math.atan(new_topleft[0]/(new_topleft[1]))
x_skew_matrix = numpy.matrix([[1, -1*math.tan(theta_x)], [0, 1]])

#run the coordinate transform for x first
new_botright = numpy.matmul(x_skew_matrix, [new_botright[0],new_botright[1]])
new_topright = numpy.matmul(x_skew_matrix, [new_topright[0],new_topright[1]])
new_topleft = numpy.matmul(x_skew_matrix, [new_topleft[0],new_topleft[1]])
#nanowire
new_nw1 = numpy.matmul(x_skew_matrix, [new_nw1[0],new_nw1[1]])
new_nw2= numpy.matmul(x_skew_matrix, [new_nw2[0],new_nw2[1]])

#print(new_botright.item(1))
theta_y = math.atan(new_botright.item(1)/(new_botright.item(0)))
y_skew_matrix = numpy.matrix([[1, 0], [-math.tan(theta_y), 1]])
#run the coordinate transform for y skew
new_botleft = numpy.matrix([0,0])
new_botright = numpy.matmul(y_skew_matrix, [new_botright.item(0),new_botright.item(1)])
print("nbr =", new_botright)
new_topright = numpy.matmul(y_skew_matrix, [new_topright.item(0),new_topright.item(1)])
print("ntr =", new_topright)
new_topleft = numpy.matmul(y_skew_matrix, [new_topleft.item(0),new_topleft.item(1)])
print("ntl =", new_topleft)

#nanowire coordinate tranform for y skew
new_nw1 = numpy.matmul(y_skew_matrix, [new_nw1.item(0),new_nw1.item(1)])
print("nw1 =", new_nw1)
new_nw2= numpy.matmul(y_skew_matrix, [new_nw2.item(0),new_nw2.item(1)])
print("nw2 =", new_nw2)


#now that everything is aligned, find the average height and width
equiv_width = (abs(new_botright.item(0)-new_botleft.item(0))+abs(new_topright.item(0)-new_topleft.item(0)))/2
equiv_height = (abs(new_topright.item(1)-new_botright.item(1))+abs(new_topleft.item(1)-new_botleft.item(1)))/2
#print("equiv_width =", equiv_width)
#print("equiv_height =", equiv_height)

#x coordinate of the nanowire
new_nw1[0,0] = (die_width/equiv_width)*new_nw1.item(0)
new_nw1[0,1] = (die_height/equiv_height)*new_nw1.item(1)
print("nw1_coords =", new_nw1)

new_nw2[0,0] = (die_width/equiv_width)*new_nw2.item(0)
new_nw2[0,1] = (die_height/equiv_height)*new_nw2.item(1)
print("nw2_coords =", new_nw2)
#THESE ARE THE COORDINATES WITH RESPECT TO THE BOTTOM LEFT HAND CORNER OF THE DIE


#can sanity check by calculating the length of the nanowire

#new_topleft = 
#new_topright = 
#the aim of this code is to extract the coordinates of the nanowire
#y_scale_1 = (abs(coord_topleft[1]- coord_botleft[1])+ abs(coord_topright[1]- coord_botright[1]))/2
#print(y_scale_1)
#x_scale_1 = (abs(coord_botright[0]- coord_botleft[0])+ abs(coord_topright[0]- coord_topleft[0]))/2
#print(x_scale_1)