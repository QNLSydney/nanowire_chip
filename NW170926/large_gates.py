import dxfwrite
from dxfwrite import DXFEngine as dxf

def plungers_side(layer, plunger_to_nw, plunger_tip_width, plunger_tip_height, plunger_taper_width,blockname): #plungers on just one side of the nanowire
	
	block  = dxf.block(blockname, layer=layer)
	taper= dxf.polyline(layer = layer)
	taper.add_vertices([(-plunger_tip_width/2,-plunger_to_nw), (plunger_tip_width/2,-plunger_to_nw),
		(plunger_taper_width/2,-plunger_tip_height-plunger_to_nw), (-plunger_taper_width/2,-plunger_tip_height-plunger_to_nw)])
	taper.close(True)
	block.add(taper)
	
	return block                                                             # creating the block


def plungers_side_mirror(layer, plunger_to_nw, plunger_tip_width, plunger_tip_height, plunger_taper_width,blockname): #plungers on just one side of the nanowire
	block  = dxf.block(blockname, layer=layer)
	
	taper= dxf.polyline(layer = layer)
	taper.add_vertices([(-plunger_tip_width/2,-plunger_to_nw), (plunger_tip_width/2,-plunger_to_nw),
		(plunger_taper_width/2,-plunger_tip_height-plunger_to_nw), (-plunger_taper_width/2,-plunger_tip_height-plunger_to_nw)])
	taper.close(True)
	block.add(taper)

	taper_top= dxf.polyline(layer = layer)
	taper_top.add_vertices([(-plunger_tip_width/2,plunger_to_nw), (plunger_tip_width/2,plunger_to_nw),
		(plunger_taper_width/2,plunger_tip_height+plunger_to_nw), (-plunger_taper_width/2, plunger_tip_height+plunger_to_nw)])
	taper_top.close(True)
	block.add(taper_top)

	return block


def position_plunger(new_blockname, blockname,layer,color, *plunger_coords):
	block = dxf.block(new_blockname, layer = layer)
	for plunger in plunger_coords:
		plunger_ref_temp = dxf.insert(blockname = blockname, insert = (plunger,0), columns = 1, rows = 1, 
    		colspacing = 0,rowspacing =0, color = color)
		block.add(plunger_ref_temp)
	
	return block    


def contacts_parallel(drawing, blockname, layer, color, taper_point, taper_length, taper_width, taper_before_track, *contact_coords): # contacts the nanowire in parallel

	block_temp = dxf.block("block_temp", layer = layer)
	drawing.blocks.add(block_temp)
	taper= dxf.polyline(layer = layer)
	taper.add_vertices([(0,-taper_point/2), (0,taper_point/2), (-taper_length,taper_width/2), (-taper_length,-taper_width/2)])
	taper.close(True)
	#drawing.add(taper)
	block_temp.add(taper)
	block_temp.add(dxf.rectangle((-taper_length-taper_before_track,-taper_width/2), taper_before_track, taper_width, 
        color = color, rotation = 0, layer = layer)) #contact 1
	#block.add(dxf.rectangle((-taper_length-taper_before_track,-taper_width/2), taper_before_track, taper_width, 
      #  color = color, rotation = 0, layer = layer)) #contact 2
	
	block = dxf.block(blockname, layer = layer)
	block_ref = dxf.insert(blockname='block_temp', insert=(contact_coords[0],0), columns = 1 , rows = 1, 
		colspacing = 0, rowspacing = 0, color =color, rotation = 0) 
	block_ref1= dxf.insert(blockname='block_temp', insert=(contact_coords[1],0), columns = 1 , rows = 1, 
		colspacing = 0, rowspacing = 0, color =color, rotation = 180) 
	block.add(block_ref)
	block.add(block_ref1)

	return block

def position_parallel_contacts(new_blockname, blockname,layer,color, rotation, *contact_coords):
	block = dxf.block(new_blockname, layer = layer)
	for contact in contact_coords:
		contact_ref_temp = dxf.insert(blockname = blockname, insert = (contact,0), columns = 1, rows = 1, 
    		colspacing = 0,rowspacing =0, color = color, rotation = rotation)
		block.add(contact_ref_temp)
	
	return block   


#def contacts_orthogonal()