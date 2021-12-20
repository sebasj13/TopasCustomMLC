# topas-create-custom-mlc

## A GUI to automatically create a TOPAS-readable MLC simulation file

Modern MLCs can have very compley leaf designs. Since not all geometries can be build using TOPAS, this script creates a custom MLC architecture from a CAD file describing a single leaf (.stl). Using a GUI, the positions of up to 64 leaf pairs can be individually customized - simply limited by the screen height. However, an arbitary amount of leaf pairs can be positioned using rectangular fields, or using presets.

## Usage

Before starting the script, a couple of options need to be set to fit the program to your .stl file.

Change the values in the \###Setup\### portion of the script to match your requirements:

- leaf_stl_path : Let TOPAS know where to find the .stl file describing the leaf
- number_of_leaf_pairs : Number of leaf pairs in the MLC
- MLC-TransZ : Distance from the Source to the top of the MLC, in cm
- SSD : Source-Surface-Distance, in cm
- dist_from_xy_plane_to_top_edge : Z-Coordinate of the .stl environment (ideally this would be 0), in mm
- dist_from_z_axis_to_inner_edge : X-/Y-Coordinate of the .stl environment (deviation from centre axis), in mm  

## Preview
 
![Preview](https://user-images.githubusercontent.com/87897942/146832691-24346005-0484-402b-82e8-90ebb472417a.png)

## Dependencies

Requires python3, numpy, and tkinter.
