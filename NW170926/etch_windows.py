import dxfwrite
from dxfwrite import DXFEngine as dxf

def double_dot_etch_block(layer, starting_gap, window_length, etch_window_1, island_1, etch_window_2, island_2, etch_window_3, blockname):
	
	block  = dxf.block(blockname, layer=layer)                                                                # creating the block
	x_etch_position = starting_gap
	block.add(dxf.rectangle((x_etch_position,-window_length/2), etch_window_1, window_length, rotation = 0, layer = layer))
	x_etch_position = starting_gap+etch_window_1+island_1
	block.add(dxf.rectangle((x_etch_position,-window_length/2), etch_window_2, window_length, rotation = 0, layer = layer))
	x_etch_position = starting_gap+etch_window_1+island_1+etch_window_2+island_2
	block.add(dxf.rectangle((x_etch_position,-window_length/2), etch_window_3, window_length, rotation = 0, layer = layer))                        # short horiztonal right
	# add block-definition to drawing
	#drawing.blocks.add(block_name)
	print("I DID IT ETCH BLOCK")
	return block
	
def initial_test_etch_block(layer, window_spacing, start_window_width, no_windows, window_length, window_size):
	block  = dxf.block("test_etch_block", layer=layer) 
	current_coordinate = window_spacing
	window_size = start_window_width
	for i in range(no_windows):
		block.add(dxf.rectangle((current_coordinate,-window_length/2), window_size, window_length, rotation = 0))
		current_coordinate += window_size + window_spacing
		window_size += window_increment
	return block