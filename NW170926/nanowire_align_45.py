import os
import sys
import math
import alignment_marker
import etch_windows
from dxfwrite import DXFEngine as dxf

name="rectangle.dxf"
drawing = dxf.drawing(name)

# LAYER 0 DETAILS
#properties of the die
die_length = 4000        #length of a single nanowire chip
die_width = 4000         #width of a single nanowire chip
align_distance = 100     #the distance of the alignment markers from the edge of the chip
no_x_align = 2      # how many alignment markers in each corner (cols)
no_y_align = 2      # how many alignment markers in each corner (cols)


#ALIGNMENT MARKERS
#which alignment markers do you want to include
am_elionix = 1     # 1 = True (include), 0 = False (don't include) - this adds the elionix alignment markers
align_space_e = 150    # this is the spacing between each
am_raith = 0       # 1 = True, 0 = False - this adds the raith alignment markers
align_space_r = 0    # this is the spacing between each
am_vistec = 1  # 1 = True, 0 = False - this adds the elionix alignment markers
align_space_v = 140    # this is the spacing between each
cc = [0,0,0]            #centre coordinate for the alignment marker

#ELIONIX ALIGNMENT MARKER PROPERTIES (individual)
width_align_e = 150
w_e = width_align_e
print("Elionix Alignment marker length = ",w_e)
padheight_e= 0.45      #this is as a proportion of the total alignment marker
ph_e = padheight_e*width_align_e
print("Elionix Pad height =", ph_e)
padwidth_e = 10.0/150          #this is as a proportion of the total alignment marker
pw_e = padwidth_e*width_align_e
print("Elionix Padwidth =" , pw_e)
tracksize_e = 0.5/150            #this is as a proportion of the total alignment marker
ts_e = tracksize_e*width_align_e
print("Elionix Tracksize =", ts_e)

#RAITH ALIGNMENT MARKER PROPERTIES (individual) # this is a simple cross
width_align_r = 0
w_r = width_align_r
print("Raith Alignment marker length = ",w_r)
padwidth_r = 0          #this is as a proportion of the total alignment marker
pw_r = padwidth_r*width_align_r
print("Raith Padwidth =" , pw_r)

#VISTEC ALIGNMENT MARKER PROPERTIES (individual) # this is just a rectangle
width_align_v = 20
w_v = width_align_v
print("Vistec Alignment marker length = ",w_v)
height_align_v = 20
h_v = height_align_v
print("Vistec Alignment marker length = ",h_v)

am_colour = 1
grid_colour = 180
etch_colour = 90
contact_colour = 250

nw_x = 2 #number of nanowires in the x direction
nw_y = 2 #number of nanowires in the y direction
nw_die_width = 300
nw_die_height = 300
nw_grid_spacing = 150

#size of the nanowire alignment markets
nw_am_width = 10
text_height = 10

#size of orientation arrow
orient_arrowhead_length = 150
orient_base_width = 40
orient_base_height = 250

#THESE ARE THE DETAILS OF THE FINE ALIGNMENT MARKERS

#FROM HERE AND BELOW YOU SHOULD NOT NEED TO EDIT ANY PARAMETERS
layer00 = 'GRIDLINES'
drawing.layers.add(dxf.layer(name=layer00, color=grid_colour))

layer0 = 'ALIGNMENT_MARKERS'
drawing.layers.add(dxf.layer(name=layer0, color=am_colour))

layer1 = 'ETCH_MARKERS'
drawing.layers.add(dxf.layer(name=layer1, color= etch_colour))

layer2 = 'SIMPLE_FIRST_CONTACTS'
drawing.layers.add(dxf.layer(name=layer2, color= contact_colour))

#AM GRID HEIGHT AND WIDTH  - figures out the block width and height
am_e_gridwidth = no_x_align*w_e +(no_x_align-1)*align_space_e
am_e_gridheight = no_y_align*w_e +(no_y_align-1)*align_space_e
print("am_e_gridheight=", am_e_gridheight)
print("am_e_gridwidth=", am_e_gridwidth)

am_r_gridwidth = no_x_align*w_r +(no_x_align-1)*align_space_r
am_r_gridheight = no_y_align*w_r +(no_y_align-1)*align_space_r
print("am_r_gridwidth=", am_r_gridwidth)
print("am_r_gridheight=", am_r_gridheight)

am_v_gridwidth = no_x_align*w_v +(no_x_align-1)*align_space_v
am_v_gridheight =no_y_align*h_v +(no_y_align-1)*align_space_v
print("am_v_gridheight=", am_v_gridheight)
print("am_v_gridwidth=", am_v_gridwidth)

#checks that the alignment markers will actually fit on the die that you have specified, taking into account which alignment markers you want to be present on the board, #am_elionix will be 0 or 1 depending
#on whether we are including that kind of alignment marker or not
if die_length < (2*align_distance+(am_e_gridheight*am_elionix+ am_r_gridheight*am_raith +am_v_gridheight*am_vistec)):
    print("The die length is not long enough to support the dimensions of your alignment markers")
    quit()
if die_width < (2*align_distance+(am_e_gridwidth*am_elionix+ am_r_gridwidth*am_raith +am_v_gridwidth*am_vistec)):
    print("The die width is not long enough to support the dimensions of your alignment markers")
    quit()

# create a block-reference
#let's define the bottom left as the (0,0) point of the drawing, in the middle of the chip such that the alignment markers are symmetric around it

#makes the elionix block
ame = alignment_marker.elionix_alignment_marker(layer0, w_e, pw_e, ph_e, ts_e, 0, 0)
drawing.blocks.add(ame)
#makes the raith block
amr = alignment_marker.raith_alignment_marker(layer0, w_r, pw_r, 0, 0)
drawing.blocks.add(amr)
#makes the vistec block
amv = alignment_marker.vistec_alignment_marker(layer0, h_v, w_v, 0, 0)
drawing.blocks.add(amv)

#ADDING ELIONIX BLOCK
am_e_x = [-die_width/2+align_distance+w_e/2, -die_width/2+align_distance+w_e/2] # defining the coordinates of the positions of the alignment blocks
am_e_y = [-die_length/2+align_distance+w_e/2, +die_length/2-align_distance-am_e_gridheight+w_e/2]

ae_ref = dxf.insert(blockname='alignmentmarker_elionix', insert=(am_e_x[0],am_e_y[0]), columns = no_x_align , rows = no_y_align, 
    colspacing = w_e+align_space_e, rowspacing = w_e+ align_space_e, layer = layer0, color =am_colour) #bot left
ae_ref1 = dxf.insert(blockname='alignmentmarker_elionix', insert=(am_e_x[1],am_e_y[1]), columns = no_x_align , rows = no_y_align, 
    colspacing = w_e+align_space_e, rowspacing = w_e+ align_space_e,  layer = layer0, color =am_colour) # top left


#ADD THE ELIONIX ORIENTATION SQUARES TO EACH OF THE ALIGNMENT MARKERS
#how to make sure the orientation of the alignment markers is correct
orient_marker_size = (w_e-2*ph_e-ts_e)/8
orient_marker_coord = -(w_e-2*ph_e-ts_e)/4-ts_e/2-orient_marker_size/2
ame_orient  = dxf.block("ame_orient", layer=layer0)

ame_orient.add(dxf.rectangle((cc[0]+orient_marker_coord,cc[1]+orient_marker_coord,0),
        orient_marker_size,orient_marker_size,color = am_colour, rotation = 0, layer = layer0))
ame_orient.add(dxf.rectangle((cc[0]+orient_marker_coord,cc[1]+(w_e+align_space_e)*(no_y_align-1)+orient_marker_coord+ts_e+(w_e-2*ph_e-ts_e)/2,0),
        orient_marker_size,orient_marker_size,color = am_colour, rotation = 0, layer = layer0))  
ame_orient.add(dxf.rectangle((cc[0]+(w_e+align_space_e)*(no_x_align-1)+orient_marker_coord+ts_e+(w_e-2*ph_e-ts_e)/2,cc[1]+orient_marker_coord,0),
        orient_marker_size,orient_marker_size,color = am_colour, rotation = 0, layer = layer0))
ame_orient.add(dxf.rectangle((cc[0]+(w_e+align_space_e)*(no_x_align-1)+orient_marker_coord+ts_e+(w_e-2*ph_e-ts_e)/2,cc[1]+(w_e+align_space_e)*(no_y_align-1)+orient_marker_coord+ts_e+(w_e-2*ph_e-ts_e)/2,0),
        orient_marker_size,orient_marker_size,color = am_colour, rotation = 0, layer = layer0))
 
drawing.blocks.add(ame_orient)

orient_marker = dxf.insert(blockname='ame_orient', insert=(am_e_x[0],am_e_y[0]), columns = 1 , rows = 1, 
    colspacing = w_e+align_space_e, rowspacing = w_e+ align_space_e, layer = layer0, color =am_colour) #bot left
orient_marker1 = dxf.insert(blockname='ame_orient', insert=(am_e_x[1],am_e_y[1]), columns = 1 , rows = 1, 
    colspacing = w_e+align_space_e, rowspacing = w_e+ align_space_e, layer = layer0, color =am_colour) #bot left
orient_marker3 = dxf.insert(blockname='ame_orient', insert=(am_e_x[0]+orient_marker_size,am_e_y[0]+orient_marker_size), columns = 1 , rows = 1, 
    colspacing = w_e+align_space_e, rowspacing = w_e+ align_space_e, layer = layer0, color =am_colour) #bot left
orient_marker4 = dxf.insert(blockname='ame_orient', insert=(am_e_x[1]+orient_marker_size,am_e_y[1]+orient_marker_size), columns = 1 , rows = 1, 
    colspacing = w_e+align_space_e, rowspacing = w_e+ align_space_e, layer = layer0, color =am_colour) #bot left

orient_marker_e = dxf.block("orient_marker_e")
orient_marker_e.add(orient_marker)
orient_marker_e.add(orient_marker1)
orient_marker_e.add(orient_marker3)
orient_marker_e.add(orient_marker4)
drawing.blocks.add(orient_marker_e)

left_orient_marker = dxf.insert(blockname='orient_marker_e', insert=(0,0), columns = 1 , rows = 1, 
        colspacing = w_v+align_space_v, rowspacing = h_v+ align_space_v, layer = layer0, color =am_colour, rotation =0)
right_orient_marker= dxf.insert(blockname='orient_marker_e', insert=(0,0), columns = 1 , rows = 1, 
        colspacing = w_v+align_space_v, rowspacing = h_v+ align_space_v, layer = layer0, color =am_colour, rotation =180)

drawing.add(left_orient_marker)
drawing.add(right_orient_marker)

#ADDING THE RAITH BLOCK
am_r_x = [am_e_x[0], am_e_x[1]]  #the x coordinates 
am_r_y = [am_e_y[0]+am_e_gridheight+align_distance+w_r/2-w_e/2, am_e_y[1]-am_r_gridheight-align_distance+w_r/2-w_e/2] # the y coordinates o

ar_ref = dxf.insert(blockname='alignmentmarker_raith', insert=(am_r_x[0],am_r_y[0]), columns = no_x_align , rows = no_y_align, 
        colspacing = w_r+align_space_r, rowspacing = w_r+ align_space_r, layer = layer0, color =am_colour)
ar_ref1 = dxf.insert(blockname='alignmentmarker_raith', insert=(am_r_x[1],am_r_y[1]), columns = no_x_align , rows = no_y_align, 
        colspacing = w_r+align_space_r, rowspacing = w_r+ align_space_r,  layer = layer0, color =am_colour)

#ADDING THE VISTEC BLOCK
am_v_x = [am_e_x[0], am_e_x[1]]  
am_v_y = [am_r_y[0]+am_r_gridheight+align_distance+w_v/2-w_r/2, am_r_y[1]-am_v_gridheight-align_distance+w_v/2-w_r/2] # the y coordinates o


av_ref = dxf.insert(blockname='alignmentmarker_vistec', insert=(am_v_x[0],am_v_y[0]), columns = no_x_align , rows = no_y_align, 
        colspacing = w_v+align_space_v, rowspacing = h_v+ align_space_v, layer = layer0, color =am_colour)
av_ref1 = dxf.insert(blockname='alignmentmarker_vistec', insert=(am_v_x[1],am_v_y[1]), columns = no_x_align , rows = no_y_align, 
        colspacing = w_v+align_space_v, rowspacing = h_v+ align_space_v,  layer = layer0, color =am_colour)

#note that the colspacing here and row spacing will not take into account the whole structure - only the bottom left hand
# add block-reference to drawing

#THIS IS THE ALIGNMENT MARKER BLOCK FOR THE BOTTOM LEFT CORNER
#this is the block with the bottom left alignment markers, which is then replicated for the others - a block within a block
blm = dxf.block("bottom_left_am")
if am_elionix == True:
    blm.add(ae_ref)
    blm.add(ae_ref1)
if am_raith== True:
    blm.add(ar_ref)
    blm.add(ar_ref1)
if am_vistec == True:
    blm.add(av_ref)
    blm.add(av_ref1)

drawing.blocks.add(blm)

blm_L = dxf.insert(blockname='bottom_left_am', insert=(0,0), columns = 1 , rows = 1, 
        colspacing = w_v+align_space_v, rowspacing = h_v+ align_space_v, layer = layer0, color =am_colour, rotation =0)
blm_R = dxf.insert(blockname='bottom_left_am', insert=(0,0), columns = 1 , rows = 1, 
        colspacing = w_v+align_space_v, rowspacing = h_v+ align_space_v, layer = layer0, color =am_colour, rotation =180)

#SMALLER ALIGNMENT MARKERS AND NANOWIRE GRID LINES
nw_grid_height = nw_die_height*nw_y + (nw_y-1)*nw_grid_spacing
nw_grid_width = nw_die_width*nw_x + (nw_x-1)*nw_grid_spacing
print("nanowire grid height =", nw_grid_height)
print("nanowire grid width =", nw_grid_width)

if nw_grid_width > (die_width - 2*nw_grid_spacing+(am_e_gridheight*am_elionix+ am_r_gridheight*am_raith +am_v_gridheight*am_vistec)):
    print("The die length is not long enough to support the dimensions of your nanowire grids")
    quit()
if nw_grid_height  > (die_length-2*nw_grid_spacing+(am_e_gridwidth*am_elionix+ am_r_gridwidth*am_raith +am_v_gridwidth*am_vistec)):
    print("The die width is not long enough to support the dimensions of your nanowire grids")
    quit()

#once these two conditions are satisfied, we need to figure out where the location of the first should be
#need to figure out the coordinates to start this block
nw_grid  = dxf.block("nanowire_gridlines")     
nw_grid.add(dxf.rectangle((cc[0]-nw_die_width/2,cc[1]-nw_die_height/2,0),nw_die_width,nw_die_height,color =grid_colour, rotation = 0,layer = layer00))
drawing.blocks.add(nw_grid)  
nw_grid_ref = dxf.insert(blockname='nanowire_gridlines', insert=(-nw_grid_width/2+nw_die_width/2,-nw_grid_height/2+nw_die_height/2), columns = nw_x , rows = nw_y, 
        colspacing = nw_die_width+nw_grid_spacing, rowspacing = nw_die_height+nw_grid_spacing, layer = layer0, color =am_colour) 


#size of the nanowire alignment markets
#nw_am_width = 10
#x coordinates of alignment markers for nanowire
start_x_nw = -nw_die_width/2
start_y_nw = -nw_die_height/2 

x_nw_am = [(start_x_nw + i*nw_am_width) for i in range(6)]
y_nw_am = [(start_y_nw + i*nw_am_width) for i in range(6)]

#making the nanowire alignment markers which will fall in each of the grids (this is just a diagonal array)
nw_alignment = dxf.block("nanowire_alignment")
for i in range(0,5):
    nw_alignment.add(dxf.rectangle((x_nw_am[i],y_nw_am[i]), nw_am_width, nw_am_width, color = am_colour, rotation = 0, layer = layer0))
drawing.blocks.add(nw_alignment)

#BUILDS EACH SMALL NANOWIRE ALIGNMENT MARKERS
#make another block to rotate
nanowire_block = dxf.block("nanowire_block")
drawing.blocks.add(nanowire_block)
#makes the diagonal array of alignment markers
rotations = (0, 90, 180, 270)
for rotation in rotations:
    orientation_block = dxf.insert(blockname='nanowire_alignment', insert=(0,0), columns = 1 , rows = 1,
        colspacing = 0, rowspacing = 0, layer = layer0, color =am_colour, rotation = rotation)
    nanowire_block.add(orientation_block)

rotations = (90,180,270,0)
for i, rotation in enumerate(rotations):
    nw_al = "nanowire_alignment%d" % (i)
    rot_block = dxf.block(nw_al)
    drawing.blocks.add(rot_block)
    rot_block.add(dxf.rectangle((x_nw_am[i+2],y_nw_am[i]), nw_am_width, nw_am_width, color = am_colour, rotation = 0, layer = layer0))
    orientation_block = dxf.insert(blockname=nw_al, insert=(0,0), columns = 1 , rows = 1,
       colspacing = 0, rowspacing = 0, layer = layer0, color =am_colour, rotation = rotation)
    nanowire_block.add(orientation_block)

small_alignment_markers_ref = dxf.insert(blockname='nanowire_block', insert=(-nw_grid_width/2+nw_die_width/2,-nw_grid_height/2+nw_die_height/2), columns = nw_x , rows = nw_y, 
    colspacing = nw_die_width+nw_grid_spacing, rowspacing = nw_die_height+nw_grid_spacing, layer = layer0, color =am_colour, rotation =0)  # bottom left
drawing.add(small_alignment_markers_ref)

#MAKE THE LABELS FOR THE GRID
text_block = dxf.block('text_block')
drawing.blocks.add(text_block)
x_text = cc[0]-nw_die_width/2-text_height
y_text = cc[1]-nw_die_height/2-text_height
#adds the text to the block
for i in range(0,nw_x):
    for j in range(0,nw_y):
        text_block.add(dxf.text("%s" % (chr(97 + i*nw_x + (nw_y-j-1))), (x_text+(nw_die_width+nw_grid_spacing)*i,y_text+(nw_die_height+nw_grid_spacing)*j), 
                height=text_height, rotation=0, layer = layer0, color = am_colour))

nw_grid_label_ref = dxf.insert(blockname='text_block', insert=(-nw_grid_width/2+nw_die_width/2,-nw_grid_height/2+nw_die_height/2), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer0, color =am_colour) 
drawing.add(nw_grid_label_ref) # add the small grid

# Add a small arrow in the corner of the drawing, for visual orientation
arrow = dxf.polyline()
orient_block = dxf.block('orient_block')
drawing.blocks.add(orient_block)
arrow.add_vertices((
    (-orient_base_width/2, 0),
    (orient_base_width/2, 0),
    (orient_base_width/2, orient_base_height),
    (orient_arrowhead_length/2, orient_base_height),
    (0, orient_base_height+orient_arrowhead_length/2),
    (-orient_arrowhead_length/2, orient_base_height),
    (-orient_base_width/2, orient_base_height),
    (-orient_base_width/2, 0)))
orient_block.add(arrow)
ref = dxf.insert(blockname='orient_block', insert=(-die_width/2 + width_align_e*no_x_align + align_space_e*no_x_align + align_distance, -die_length/2 + align_distance), layer=layer0)
drawing.add(ref)

#this is the code which adds the first practice contacts for the nanowire #layer2

taper_point = 2 #the width of the contact at its narrowest point
taper_length = 40
taper_width = 5
taper_before_track = 10 # this is the length of the track which will stick out parallel to the nanowire
bondpad_height = 25
bondpad_width = 45

contact_block = dxf.block('contact_block')
drawing.blocks.add(contact_block)
taper= dxf.polyline(layer = layer2)
taper.add_vertices([(0,-taper_point/2), (0,taper_point/2), (-taper_length,taper_width/2), (-taper_length,-taper_width/2)])
taper.close(True)
#drawing.add(taper)
contact_block.add(taper)
contact_block.add(dxf.rectangle((-taper_length-taper_before_track,-taper_width/2), taper_before_track, taper_width, 
        color = contact_colour, rotation = 0, layer = layer2))

#drawing.add(contact_block_ref)
#creating the block for the bondpads
bondpad_block = dxf.block('bondpad_block')
drawing.blocks.add(bondpad_block)
bondpad_base= dxf.polyline(layer = layer2)
bondpad_base.add_vertices([(-bondpad_width/2,bondpad_height),(-bondpad_width/2,0),(+bondpad_width/2,0),(+bondpad_width/2,bondpad_height)])
bondpad_block.add(bondpad_base)

spline_points = [(-bondpad_width/2,bondpad_height), 
    (-bondpad_width/2+(bondpad_width-taper_width)/8,bondpad_height*2.2/2), 
    (-bondpad_width/2+(bondpad_width-taper_width)*0.8/2,bondpad_height*3/2), 
    (-bondpad_width/2+(bondpad_width-taper_width)/2,2*bondpad_height)]
bondpad_block.add(dxf.spline(spline_points, color=contact_colour, layer = layer2))

#right spline
spline_points = [(+bondpad_width/2,bondpad_height), 
    (+bondpad_width/2-(bondpad_width-taper_width)/8,bondpad_height*2.2/2), 
    (+bondpad_width/2-(bondpad_width-taper_width)*0.8/2,bondpad_height*3/2), 
    (+bondpad_width/2-(bondpad_width-taper_width)/2,2*bondpad_height)]
bondpad_block.add(dxf.spline(spline_points, color=contact_colour, layer = layer2))
bondpad_block_ref = dxf.insert(blockname='bondpad_block', insert=(-taper_length-taper_before_track-2*bondpad_height,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 270)
contact_block.add(bondpad_block_ref)

contact_block_ref= dxf.insert(blockname='contact_block', insert=(0,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 0) 

#drawing.add(bondpad_block_ref)

#feed in the coordinates of the corner of the nanowire and make the etch tests
#need to identify which nanowire it was. 
#also maybe I want to output a text file with the original, such that at least all the parameters are saved
#these coordinates will be with respect to the alignment markers - letting the bottom left corner of the subdie be the (0,0) point

window_length = 10 # height of rectangle which will be opened up over nanowire
start_window_width = 0.02 # let's start with 20nm
no_windows = 5
window_spacing = 2 #distance between windows
window_increment = 0.04

#length_windows = window_spacing*(no_windows-1)+ # NEED TO FIGURE OUT THE SUM OF A SERIES HERE
#length_nanowire = math.sqrt((nw_corner_x[0]-nw_corner_x[1])**2+(nw_corner_y[0]-nw_corner_y[1])**2)

etch_block = dxf.block('etch_block')
drawing.blocks.add(etch_block)

#this generatest the generic window to go everywhere (window_length/2 is to ensure that the grid is centred on the nanowire, and there is +window spacing at the start)
current_coordinate = window_spacing
window_size = start_window_width
for i in range(no_windows):
    etch_block.add(dxf.rectangle((current_coordinate,-window_length/2), window_size, window_length, 
        color = etch_colour, rotation = 0, layer = layer1))
    current_coordinate += window_size + window_spacing
    window_size += window_increment
#have use [0] here to place nanowire, hence need to rotate around the 0 coordinate
#NOTE THAT THIS ONLY WORKS FOR FOUR NANOWIRES - NEED TO MAKE THIS SECTION OF THE CODE MORE GENERIC

#this is the etch block for the double dots

starting_gap = 1.5 #how many ums into (+ve) or before (-ve) the start of the nanowire you want to start the etch
etch_window_1 = 0.75# the length of the first etch window
etch_window_2 = 0.02 # this is how long the island will be
etch_window_3 = 0.75
island_1 = 0.5
island_2 = 0.5

dd_etch_block_A = etch_windows.double_dot_etch_block(layer1, starting_gap, window_length, 
    etch_window_1, island_1, etch_window_2, island_2, etch_window_3, "dd_etch_block_A")
drawing.blocks.add(dd_etch_block_A) #adds the double dot etch blocks
island_1 = 1
island_2 = 1
dd_etch_block_B = etch_windows.double_dot_etch_block(layer1, starting_gap, window_length, 
    etch_window_1, island_1, etch_window_2, island_2, etch_window_3,"dd_etch_block_B")
drawing.blocks.add(dd_etch_block_B)
island_1 = 2
island_2 = 2 #adds the double dot etch blocks
dd_etch_block_C = etch_windows.double_dot_etch_block(layer1, starting_gap, window_length, 
    etch_window_1, island_1, etch_window_2, island_2, etch_window_3,"dd_etch_block_C")
drawing.blocks.add(dd_etch_block_C) #adds the double dot etch blocks
island_1 = 3
island_2 = 3
dd_etch_block_D = etch_windows.double_dot_etch_block(layer1, starting_gap, window_length, 
    etch_window_1, island_1, etch_window_2, island_2, etch_window_3,"dd_etch_block_D")
drawing.blocks.add(dd_etch_block_D) #adds the double dot etch blocks

#007
#nw1_coords = [[ 187.11635449  163.98085444]]
#nw2_coords = [[ 196.82563065  161.41557283]]
etch_block_A = dxf.block('etch_block_A')
drawing.blocks.add(etch_block_A)
#etch_block_A.add(etch_block) #adds the basis of the windows
#then adds the tapers
current_coordinate = window_spacing
window_size = start_window_width
for i in range(no_windows):
    etch_block_A.add(dxf.rectangle((current_coordinate,-window_length/2), window_size, window_length, 
        color = etch_colour, rotation = 0, layer = layer1))
    
    if i == 0:
        contact_block_ref= dxf.insert(blockname='contact_block', insert=(current_coordinate-window_spacing/2,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 0) 
        etch_block_A.add(contact_block_ref)

    if i == 1:
        contact_block_ref= dxf.insert(blockname='contact_block', insert=(current_coordinate-window_spacing/2,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 180) 
        etch_block_A.add(contact_block_ref)

    current_coordinate += window_size + window_spacing
    window_size += window_increment
#nw1_coords = [[  79.13681392  228.6861349 ]]
#nw2_coords = [[  78.63076676  218.03240404]]
nw_corner_x = (78.63076676,79.13681392)
nw_corner_y = (218.03240404,228.6861349)
nw_rotation = math.atan((nw_corner_y[1]-nw_corner_y[0])/(nw_corner_x[1]-nw_corner_x[0]))*180/math.pi #needs to be in degrees for dxfengine
print('nw rotation = ', nw_rotation)
etch_block_ref_A = dxf.insert(blockname='dd_etch_block_A', insert=(-nw_grid_width/2+nw_corner_x[0],-nw_grid_height/2+nw_die_height+nw_grid_spacing+nw_corner_y[0]), 
    columns = 1 , rows = 1, colspacing = 0, rowspacing = 0, color =am_colour, rotation = nw_rotation) 
drawing.add(etch_block_ref_A)



#B BLOCK
etch_block_B = dxf.block('etch_block_B')
drawing.blocks.add(etch_block_B)
#etch_block_A.add(etch_block) #adds the basis of the windows
#then adds the tapers
current_coordinate = window_spacing
window_size = start_window_width
for i in range(no_windows):
    etch_block_B.add(dxf.rectangle((current_coordinate,-window_length/2), window_size, window_length, 
        color = etch_colour, rotation = 0, layer = layer1))
    
    if i == 0:
        contact_block_ref= dxf.insert(blockname='contact_block', insert=(current_coordinate-window_spacing/2,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 0) 
        etch_block_B.add(contact_block_ref)

    if i == 1:
        contact_block_ref= dxf.insert(blockname='contact_block', insert=(current_coordinate-window_spacing/2,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 180) 
        etch_block_B.add(contact_block_ref)

    current_coordinate += window_size + window_spacing
    window_size += window_increment
#nw1_coords = [[ 214.48420103  198.02962153]]
#w2_coords = [[ 210.12557603  207.78701521]]

nw_corner_x = (210.12557603,214.48420103)
nw_corner_y = (207.78701521,198.02962153)
nw_rotation = math.atan((nw_corner_y[1]-nw_corner_y[0])/(nw_corner_x[1]-nw_corner_x[0]))*180/math.pi #needs to be in degrees for dxfengine
print('nw rotation = ', nw_rotation)
etch_block_ref_B = dxf.insert(blockname='dd_etch_block_B', insert=(-nw_grid_width/2+nw_corner_x[0],-nw_grid_height/2+nw_corner_y[0]), columns = 1 , rows = 1, 
    colspacing = 0, rowspacing = 0, layer = layer1, color =am_colour, rotation = nw_rotation) 
drawing.add(etch_block_ref_B)

#C BLOCK
etch_block_C= dxf.block('etch_block_C')
drawing.blocks.add(etch_block_C)
#etch_block_A.add(etch_block) #adds the basis of the windows
#then adds the tapers
current_coordinate = window_spacing
window_size = start_window_width
for i in range(no_windows):
    etch_block_C.add(dxf.rectangle((current_coordinate,-window_length/2), window_size, window_length, 
        color = etch_colour, rotation = 0, layer = layer1))
    
    if i == 0:
        contact_block_ref= dxf.insert(blockname='contact_block', insert=(current_coordinate+window_size+0.1,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 0) 
        etch_block_C.add(contact_block_ref)

    if i == 2:
        contact_block_ref= dxf.insert(blockname='contact_block', insert=(current_coordinate-0.1,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 180) 
        etch_block_C.add(contact_block_ref)

    current_coordinate += window_size + window_spacing
    window_size += window_increment

#nw1_coords = [[ 161.94765653  121.15291822]]
#nw2_coords = [[ 155.31623167  126.50788526]]
#nw1_coords = [[ 152.15989714  209.75303947]]
#nw2_coords = [[ 157.47528394  218.37590585]]
nw_corner_x = (152.15989714 ,157.47528394 )
nw_corner_y = (209.75303947,218.37590585)
nw_rotation = math.atan((nw_corner_y[1]-nw_corner_y[0])/(nw_corner_x[1]-nw_corner_x[0]))*180/math.pi #needs to be in degrees for dxfengine
print('nw rotation = ', nw_rotation)
etch_block_ref_C = dxf.insert(blockname='dd_etch_block_C', insert=(-nw_grid_width/2+nw_die_width+nw_grid_spacing+ nw_corner_x[0],-nw_grid_height/2+nw_die_height+nw_grid_spacing+nw_corner_y[0]), 
    columns = 1 , rows = 1, colspacing = 0, rowspacing = 0, layer = layer1, color =am_colour, rotation = nw_rotation) 
drawing.add(etch_block_ref_C)


#D BLOCK
etch_block_D= dxf.block('etch_block_D')
drawing.blocks.add(etch_block_D)
#etch_block_A.add(etch_block) #adds the basis of the windows
#then adds the tapers
current_coordinate = window_spacing
window_size = start_window_width
for i in range(no_windows):
    etch_block_D.add(dxf.rectangle((current_coordinate,-window_length/2), window_size, window_length, 
        color = etch_colour, rotation = 0, layer = layer1))
    
    if i == 0:
        contact_block_ref= dxf.insert(blockname='contact_block', insert=(current_coordinate+window_size+0.1,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 0) 
        etch_block_D.add(contact_block_ref)

    if i == 2:
        contact_block_ref= dxf.insert(blockname='contact_block', insert=(current_coordinate-0.1,0), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer2, color =contact_colour, rotation = 180) 
        etch_block_D.add(contact_block_ref)

    current_coordinate += window_size + window_spacing
    window_size += window_increment
#nw1_coords = [[  75.73917036  143.5991572 ]]
#nw2_coords = [[  69.18436034  151.21427983]]
#nw1_coords = [[  84.12921625  103.50261845]]
#nw2_coords = [[  80.41647313  112.93147086]]
nw_corner_x = ( 80.41647313,84.12921625 )
nw_corner_y = (112.93147086,103.50261845)
nw_rotation = math.atan((nw_corner_y[1]-nw_corner_y[0])/(nw_corner_x[1]-nw_corner_x[0]))*180/math.pi #needs to be in degrees for dxfengine
print('nw rotation = ', nw_rotation)
etch_block_ref_D = dxf.insert(blockname='dd_etch_block_D', insert=(-nw_grid_width/2+nw_die_width+nw_grid_spacing+nw_corner_x[0],-nw_grid_height/2+nw_corner_y[0]), columns = 1 , rows = 1, 
        colspacing = 0, rowspacing = 0, layer = layer1, color =am_colour, rotation = nw_rotation) 
drawing.add(etch_block_ref_D)


#ASSEMBLE THE DRAWING
#add the grid lines for the design
drawing.add(nw_grid_ref) # add the small grid
drawing.add(blm_L) #adding the alignment markers
drawing.add(blm_R) 

#adding the grid lines
drawing.add(dxf.rectangle((-die_width/2, -die_length/2),die_width, die_length, color = grid_colour,rotation = 0, layer = layer00)) #makes the outline of the chip
drawing.add(dxf.line(start = (-die_width/2, -die_length/2), end = (+die_width/2, +die_length/2), color = grid_colour, layer = layer00)) #adds lines which should cross at zero
drawing.add(dxf.line(start = (-die_width/2, +die_length/2), end = (+die_width/2, -die_length/2), color = grid_colour,layer = layer00)) #adds lines which should cross at zero

drawing.save()
print("drawing '%s' created.\n" % name)
exit(0)
