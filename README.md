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
|   gen_id.py - Python script to generate id's, to be copied into 4inch_Layout_wxhid.ftxt files.
|   coordinate_transform.py - Takes the coordinates of the nanowire in Photoshop and translates to mask.
+---Generated Write Files
    |   Contains historical generated files
```

### Building an alignment layer
To build the alignment layer:

1. Run `nanowire_align.py`. This will generate `rectangle.dxf`.
2. Open `4inch_layout.ftxt`. Edit the "GenJobdesk" step as appropriate. ID's will not yet be included.
3. Run `gen_id.py` changing X&Y in the script to the dimensions of the written chip. This generates `ids.txt`.
4. Copy `4inch_layout.ftxt` to `4inch_Layout_<w>x<h>id.ftxt`, and replace the `TEXT_VALUES` section  
   of the file with the values generated into `ids.txt`.
5. Run beamer to generate output CON file. (Note: Will need to get values of dwell time from WECAS)
