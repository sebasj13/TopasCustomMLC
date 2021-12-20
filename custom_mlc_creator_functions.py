# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 16:21:35 2021

@author: Sebastian Schäfer
@institution: Martin-Luther-Universität Halle-Wittenberg
@email: sebastian.schaefer@student.uni-halle.de
"""

import re
import os
import numpy as np
import tkinter as tk
from tkSliderWidget import Slider


###TOPAS Simulation File Format with Blanks###

materials = '\
#==========================MATERIALS==========================#\n\n\
sv:Ma/LeafMaterial/Components   = 3 "Tungsten" "Nickel" "Iron"\n\
uv:Ma/LeafMaterial/Fractions 	= 3 0.95 00.0375 0.0125\n\
d:Ma/LeafMaterial/Density       = 18 g/cm3\n\n'

mlcgroup = '\
#=================MLC GROUP===============#\n\n\
s:Ge/MLCGroup/Type              = "Group"\n\
s:Ge/MLCGroup/Parent        	= "World"\n\
d:Ge/MLCGroup/TransZ            = {} cm\n\n' 

placement_left = '\
#===============PLACEMENT GROUP=============#\n\n\
s:Ge/LeftGroup/Type 	    	= "Group"\n\
s:Ge/LeftGroup/Parent       	= "MLCGroup"\n\
d:Ge/LeftGroup/RotX             = 180 deg\n\
d:Ge/LeftGroup/TransZ	    	= {} mm\n\n' 

placement_right = '\
s:Ge/RightGroup/Type        	= "Group"\n\
s:Ge/RightGroup/Parent 	    	= "MLCGroup"\n\
d:Ge/RightGroup/RotY 	    	= 180 deg\n\
d:Ge/RightGroup/TransZ	    	= {} mm\n\n\
#===================COMPONENTS===============#\n\n' 

left_leaf_parameters    = '\
s:Ge/LeftLeaf{}/Type             = "TsCAD"\n\
s:Ge/LeftLeaf{}/Parent           = "LeftGroup"\n\
s:Ge/LeftLeaf{}/Material         = "LeafMaterial"\n\
d:Ge/LeftLeaf{}/TransX           = {} mm\n\
d:Ge/LeftLeaf{}/TransY           = {} mm\n\
d:Ge/LeftLeaf{}/TransZ           = {} cm\n\
d:Ge/LeftLeaf{}/RotX             = {} deg\n\
s:Ge/LeftLeaf{}/DrawingStyle     = "Solid"\n\
s:Ge/LeftLeaf{}/InputFile        = "{}"\n\
s:Ge/LeftLeaf{}/FileFormat       = "stl" \n\
d:Ge/LeftLeaf{}/Units            = 1 mm\n\
s:Ge/LeftLeaf{}/Color            = {}\n\n'

right_leaf_parameters   = '\
s:Ge/RightLeaf{}/Type            = "TsCAD"\n\
s:Ge/RightLeaf{}/Parent          = "RightGroup"\n\
s:Ge/RightLeaf{}/Material        = "LeafMaterial"\n\
d:Ge/RightLeaf{}/TransX          = {} mm\n\
d:Ge/RightLeaf{}/TransY          = {} mm\n\
d:Ge/RightLeaf{}/TransZ          = {} cm\n\
d:Ge/RightLeaf{}/RotX            = {} deg\n\
s:Ge/RightLeaf{}/DrawingStyle    = "Solid"\n\
s:Ge/RightLeaf{}/InputFile       = "{}"\n\
s:Ge/RightLeaf{}/FileFormat      = "stl"\n\
d:Ge/RightLeaf{}/Units           = 1 mm\n\
s:Ge/RightLeaf{}/Color           = {}\n\n'

def load_mlc_data(input):

    """
    A function that loads specified MLC leaf positions from a
    numpy .txt file and creates the according simulation file.
    """

    ###################SETUP###################

    leaf_stl_path = ""                                                                                #Path to single leaf .stl file
    number_of_leaf_pairs = 80                                                                         #Amount of leaf pairs in MLC configuration
    MLC_TransZ = 0 #cm                                                                                #Translation distance of whole MLC along Z
    SSD = 100 #cm                                                                                     #Source-Surface-Distance
    dist_from_xy_plane_to_top_edge = 0 #mm                                                            #Correction amount from stl coordinates to TOPAS (z-axis)
    dist_from_z_axis_to_inner_edge = 0 #mm                                                            #Correction amount from stl coordinates to TOPAS (x/y-axis)
   
    ###########################################

    if os.path.exists(input) != True:
        return
    
    leaf_positions = np.loadtxt(input)                                                                #Load .txt file and initialize lists for the leaf banks
    leaf_positions = leaf_positions.tolist()
    leafpositions_left = []
    leafpositions_right = []

    for value in leaf_positions:                                            

        value = sorted(value)                                                                         #Assing value to correct leaf bank

        if value[0] != 0:
            pos_left  = 2*value[0]/abs(value[0])*field_size_calc(abs(value[0]), SSD, MLC_TransZ)      #Field size calculation, special case for size 0
        
        else:
            pos_left = 0

        if value[1] != 0:

            pos_right = -2*value[1]/abs(value[1])*field_size_calc(abs(value[1]),SSD, MLC_TransZ)      #Field size calculation, special case for size 0
        else:
            pos_right = 0

        leafpositions_left  += [round(-(dist_from_z_axis_to_inner_edge-pos_left),3)]                  #Account for the 180° rotation of the leaf bank placement
        leafpositions_right += [round(-(dist_from_z_axis_to_inner_edge-pos_right),3)]

    leafpositions_right.reverse()    
    TransX = [leafpositions_left, leafpositions_right]
    
    CreateTopasMLCFile("DICOM_MLC_POS.txt", leaf_stl_path, number_of_leaf_pairs, MLC_TransZ, TransX)  #Write TOPAS simulation file 

    return

def field_size_calc(field_size, SSD, TransZ):

    """
    A function that calculates the desired field size using the intercept theorem.
    """

    return (TransZ/SSD) *field_size

def CreateTopasMLCFile(filename: str, leaf_stl_path: str, number_of_leaf_pairs: int, \
    dist_from_xy_plane_to_top_edge: int, MLC_TransZ: int, TransX: list, \
    materials = materials, mlcgroup = mlcgroup, placement_left = placement_left, \
    placement_right = placement_right): 

    """
    A function that uses the specified parameters to create a TOPAS-readable simulation file
    for a MLC. Needs a .stl (3D) file describing one leaf and the desired positioning info
    to the place many of these in the correct positions.
    """

    TransY  = [2*i+2/2 for i in range(-int(number_of_leaf_pairs/2),int(number_of_leaf_pairs/2))]      #Space between leaves
    TransYR = TransY                                                                                  #Identical for both leaf banks
    TransZ  = [0 for i in range(-int(number_of_leaf_pairs/2),int(number_of_leaf_pairs/2))]            #Rotation correction - example: [5*np.cos(0.005*i) for i in range(-int(number_of_leaf_pairs/2),int(number_of_leaf_pairs/2))]
    RotX    = [180 for i in range(number_of_leaf_pairs)]                                              #Leaf angles - example: np.linspace(168,192,number_of_leaf_pairs).tolist()

    RotXR = RotX                                                                                      #Identical for both leaf banks

    leftcolors  = ['"Grey080"','"Grey160"']*int(number_of_leaf_pairs/2)                               #Alternating color scheme for leaves                                              
    rightcolors  = ['"Grey080"','"Grey160"']*int(number_of_leaf_pairs/2)

    leaf_num = number_of_leaf_pairs

    with open(filename,"w+") as file:   

        file.writelines(materials)                                                                    #Write header containing the MLC group information, materials etc.
        file.writelines(mlcgroup.format(MLC_TransZ))
        file.writelines(placement_left.format(dist_from_xy_plane_to_top_edge))
        file.writelines(placement_right.format(dist_from_xy_plane_to_top_edge))

        for i in range(leaf_num):                                                                     #Write the position of each individual leaf
            file.writelines(left_leaf_parameters.format(i,i,i,i,TransX[0][i],i,TransY[i], \
                i,TransZ[i],i,RotX[i],i,i,leaf_stl_path,i,i,i,leftcolors[i]))

            file.writelines(right_leaf_parameters.format(i,i,i,i,TransX[1][leaf_num-1-i], \
                i,TransYR[leaf_num-1-i],i,TransZ[leaf_num-1-i],i,RotXR[leaf_num-1-i],i,i, \
                leaf_stl_path,i,i,i,rightcolors[i]))

    return

def set_vals(sliders):

    """
    A function that sets a LeafSlider to a specified value.
    """

    for slider in sliders:
        slider.update_val()
        slider.entry.delete(0, 'end')
    return

class LeafSlider(Slider):

    """
    A class describing selector with two sliders, imitation a MLC leaf pair.
    """
              
    def __init__(self,root,row,values=[-5,5]):
        
        self.root = root
        self.row = (40+row*15)         
        self.current_value = tk.DoubleVar()
        self.mystring =tk.StringVar(root)
        self.slider = Slider(self.root, width = 750, height = 19, min_val = -20, max_val = 20, init_lis = values, show_value = True)
        self.slider.pack()
        self.slider.place(y= self.row)
        self.entry = tk.Entry(self.root, textvariable = self.mystring)
        self.entry.pack()
        self.entry.place(x=760,y=self.row)

    def update_val(self):

        """
        A method to change the value of a LeafSlider.
        """
        
        input = self.mystring.get()
        negint = re.findall(r"-[0-9]+", input)
        b = re.findall(r"[-+]?\d*\.\d+|\d+", input)
        for num in negint:
            for flt in b:
                if float(num) == - float(flt):
                    b.remove(flt)
        b += negint
        
        if len(b)!= 2:
            b = self.slider.getValues()
            self.slider.destroy()
            self.slider = Slider(self.root, width = 750, height = 19, min_val = -20, max_val = 20, init_lis = b, show_value = True)
            self.slider.pack()
            self.slider.place(y= self.row)
            return

        c = [float(b[0]),float(b[1])]
        self.slider.destroy()
        self.slider = Slider(self.root, width = 750, height = 19, min_val = -20, max_val = 20, init_lis = c, show_value = True)
        self.slider.pack()
        self.slider.place(y= self.row)
        return