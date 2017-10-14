import dxfwrite
from dxfwrite import DXFEngine as dxf

def elionix_alignment_marker(layer, w_e, pw_e, ph_e,ts_e,cc_x,cc_y): #program does nothing as written
    #questions: does the layer name have to be a string?
    #In this case, the alignment marker elionix block will always be called the elionix block
	cc = [cc_x,cc_y]
	block  = dxf.block("alignmentmarker_elionix", layer=layer)                                                                # creating the block
	block.add(dxf.rectangle((cc[0]-pw_e/2,cc[1]-w_e/2,0),pw_e,ph_e, rotation = 0))          #bottom square of alignment marker
	block.add(dxf.rectangle((cc[0]-w_e/2,cc[1]-pw_e/2,0),ph_e,pw_e, rotation = 0))          # left square
	block.add(dxf.rectangle((cc[0]-pw_e/2,cc[1]+w_e/2-ph_e,0),pw_e,ph_e, rotation = 0))     # top square
	block.add(dxf.rectangle((cc[0]+w_e/2-ph_e,cc[1]-pw_e/2,0),ph_e,pw_e, rotation = 0))    # right square
	block.add(dxf.rectangle((cc[0]-ts_e/2,cc[1]-w_e/2+ph_e,0),ts_e,w_e-2*ph_e, rotation = 0))                                # long vertical
	block.add(dxf.rectangle((cc[0]-ts_e/2-(w_e-2*ph_e-ts_e)/2,cc[1]-ts_e/2,0),(w_e-2*ph_e-ts_e)/2,ts_e, rotation = 0))         # short horizonal left
	block.add(dxf.rectangle((cc[0]+ts_e/2,cc[1]-ts_e/2,0),(w_e-2*ph_e-ts_e)/2,ts_e, rotation = 0))                            # short horiztonal right
	# add block-definition to drawing
	#drawing.blocks.add(block_name)
	print("I DID IT ELIONIX")
	return block


def raith_alignment_marker(layer, w_r, pw_r, cc_x, cc_y): #program does nothing as written
    #questions: does the layer name have to be a string?
    #In this case, the alignment marker elionix block will always be called the elionix block
	cc = [cc_x,cc_y]
	block  = dxf.block("alignmentmarker_raith", layer=layer)                                                                # creating the block
	block.add(dxf.rectangle((cc[0]-pw_r/2,cc[1]-w_r/2,0),pw_r,w_r, rotation = 0,layer = layer))                                # long vertical
	block.add(dxf.rectangle((cc[0]-w_r/2,cc[1]-pw_r/2,0),(w_r-2-pw_r)/2,pw_r, rotation = 0,layer = layer))               # short horizonal left
	block.add(dxf.rectangle((cc[0]+pw_r/2,cc[1]-pw_r/2,0),(w_r-2-pw_r)/2,pw_r, rotation = 0,layer = layer))                 # short horiztonal right
	# add block-definition to drawing
	#drawing.blocks.add(block_name)
	print("I DID IT RAITH")
	return block
 
def vistec_alignment_marker(layer, h_v, w_v, cc_x, cc_y): #program does nothing as written
	cc = [cc_x,cc_y]
	block  = dxf.block("alignmentmarker_vistec", layer=layer)                                                                # creating the block
	block.add(dxf.rectangle((cc[0]-w_v/2,cc[1]-h_v/2,0),w_v,h_v, rotation = 0,layer = layer))   # long vertical
	print("I DID IT VISTEC")
	return block