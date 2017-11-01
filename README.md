# Nanowire Pattern Generation Repository

Scripts used for generation of nanowire chips.

Currently this only includes code for the generation of alignment
marks, however the intention is to include scripts for additional
layers.

### Files
```
nanowire_chip
|   README.md
|   nanowire_align.py - Code used to generate the base unit of the chip
|                       note: this is currently only the alignment marks layer.
|   4inch_Layout.ftxt - Base Beamer script to place chip into a wafer layout
|   4inch_Layout_wxhid.ftxt - Beamer script which includes ID's for a w x h wafer.
|   gen_layout.py - Python script to generate wafer layouts's, to be copied into 4inch_Layout_wxhid.ftxt files.
|   coordinate_transform.py - Takes the coordinates of the nanowire in Photoshop and translates to mask.
+---Generated Write Files
    |   Contains historical generated files
```

### Building an alignment layer
To build the alignment layer:

1. Run `nanowire_align.py`. This will generate `rectangle.dxf`.
2. Run `gen_layout.py` passing in the the dxf, id and output filename. Options can be modified as appropriate.
   Example: `python3 gen_layout.py NW171026 rectangle.dxf Output.ftxt -x12 -y12`
3. Run beamer to generate output CON file. (Note: Will need to get values of dwell time from WECAS)
