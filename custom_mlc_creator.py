# -*- coding: utf-8 -*-
"""
Created on Fri Nov 26 12:41:44 2021

@author: Sebastian Schäfer
@institution: Martin-Luther-Universität Halle-Wittenberg
@email: sebastian.schaefer@student.uni-halle.de
"""

import sys
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from custom_mlc_creator_functions import *

###################SETUP###################

leaf_stl_path = ""                                                                                                    #Path to single leaf .stl file
number_of_leaf_pairs = 64                                                                                             #Amount of leaf pairs in MLC configuration (Max to render: 64)
MLC_TransZ = 0 #cm                                                                                                    #Translation distance of whole MLC along Z
SSD = 100 #cm                                                                                                         #Source-Surface-Distance
dist_from_xy_plane_to_top_edge = 0 #mm                                                                                #Correction amount from stl coordinates to TOPAS (z-axis)
dist_from_z_axis_to_inner_edge = 0 #mm                                                                                #Correction amount from stl coordinates to TOPAS (x/y-axis)

###########################################

##################PRESETS##################

sine = [[5 + 10*np.sin(i*np.pi/15),-5 +10*np.sin(i*np.pi/15)] for i in range(-32,32)]                                 #Preset for a sinusoid field
wave = [[10*np.cos(i*np.pi/15),-10*np.cos(i*np.pi/15)] for i in range(-32,32)] + [[0,0] for i in range(0)]            #Preset for a wave field
zigzag = [[-5,5] if i%2==0 else  [0,0] for i in range(-32,32) ]                                                       #Preset for a open-close-open-close field
diag = [[i*0.5-2.5,i*0.5+2.5] for i in range(-32,32)]                                                                 #Preset for a diagonal field

###################SETUP###################

def CalculateLeafPositions(leaf_num, leaf_stl_path, number_of_leaf_pairs, MLC_TransZ, SSD, \
    dist_from_xy_plane_to_top_edge, dist_from_z_axis_to_inner_edge, root):
    
    """
    Function that calculates the correct MLC positioning in the simulated coordinate system. 
    Uses the specified field_size_calc() function to transform the desired field size into
    the opening distance of each leaf. Standard setup uses the intercept theorem, however
    this function can be replaced as necessary.

    Calls the imported CreateTopasMLCFile() function to create the build MLC simulation file.
    """

    global sliders

    if number_of_leaf_pairs >= leaf_num:                                                                              #Since only 64 leaves fit on screen, set the position
                                                                                                                      #of all others to 0 if more exist
        leafpositions_left = [-dist_from_z_axis_to_inner_edge for i in range(0,(number_of_leaf_pairs-leaf_num)//2)]   
        leafpositions_right = [-dist_from_z_axis_to_inner_edge for i in range(0,(number_of_leaf_pairs-leaf_num)//2)]  

    for leafslider in sliders:

        slidervalues         = sorted(leafslider.slider.getValues())                                                  #Read desired leaf positions from the slider positions

        field_size = abs(slidervalues[1]-slidervalues[0])                                                             #Calculate the field size from the two positions
        offset = (slidervalues[1]+slidervalues[0])/2                                                                  #Calculate the centre-axis-offset from the two positions

        pos_right = field_size_calc(offset+field_size/2, SSD, MLC_TransZ)                                             #Calculate the according distance from the centre axis
        pos_left = field_size_calc(-offset+field_size/2, SSD, MLC_TransZ)                                             #for both leaves

        leafpositions_left  += [round(-(dist_from_z_axis_to_inner_edge+pos_left),3)]                                 #Set the according positions of the leaves while accounting
        leafpositions_right += [round(-(dist_from_z_axis_to_inner_edge+pos_right),3)]                                #for differences between the two coordinate systems

    if number_of_leaf_pairs >= leaf_num:                                                                             #Since only 64 leaves fit on screen, set the position
                                                                                                                     #of all others to 0 if more exist
        leafpositions_left += [-dist_from_z_axis_to_inner_edge for i in range(number_of_leaf_pairs-\
            (number_of_leaf_pairs-leaf_num)//2,number_of_leaf_pairs)]                                                 

        leafpositions_right += [-dist_from_z_axis_to_inner_edge for i in range(number_of_leaf_pairs-\
            (number_of_leaf_pairs-leaf_num)//2,number_of_leaf_pairs)]                                                 

    leafpositions_right.reverse()                                                                                    #Account for the 180° rotation of the leaf bank placement

    CreateTopasMLCFile("Custom_MLC.txt", leaf_stl_path, number_of_leaf_pairs, \
        dist_from_xy_plane_to_top_edge, MLC_TransZ, [leafpositions_left,leafpositions_right])                        #Write TOPAS simulation file

    root.destroy()                                                                                                   #Close after job
    
    return

def main(): 

    """
    Function that defines the GUI and its components to customize a MLC for a TOPAS simulation. 
    """

    if number_of_leaf_pairs >=64:
        number_of_rendered_leafs = 64
    else:
        number_of_rendered_leafs = number_of_leaf_pairs
    
    global sliders 
    
    def choose_preset(root, preset=None):
        
        """
        A function that sets all available sliders to a desired field size.
        """
        
        global sliders

        try: 
            if preset == None:                                                                                        #Check if preset was selected           
                x = float(e1.get())/2                                                                                 #Read value from entry field
                e1.delete(0, 'end')                                                                                   #Clear entry field for next entry
                preset = [[-x,x] for i in range(-int(len(sliders)/2),int(len(sliders)/2))]                            #Create the desired field size preset list
                
            [slider.slider.destroy() for slider in sliders]                                                           #Rebuild the sliders with the desired field size
            sliders = [LeafSlider(root,i,preset[i]) for i in range(len(sliders))]
        except Exception:
            pass
        return
    
    def move_field(root):

        """
        A function that moves the field positions of all sliders by a specified offset.
        """
        
        global sliders
        
        cur_pos = [slider.slider.getValues() for slider in sliders]                                                   #Get the current values
    
        x = float(e2.get())                                                                                           #Read value from entry field
        if x >= 20:                                                                                                   #Maximum allowed field size : 40x40
            return
        
        e2.delete(0, 'end')                                                                                           #Clear entry field for next entry

        for pos in cur_pos:                                                                                           #Add desired offset to each slider
            pos[0] += x
            pos[1] += x
            
        if np.max(cur_pos) > 20 or np.min(cur_pos) < -20:                                                             #Maximum allowed field size : 40x40
               return
          
        [slider.slider.destroy() for slider in sliders]                                                               #Rebuild the sliders with the desired field position
        sliders = [LeafSlider(root,i,cur_pos[i]) for i in range(len(sliders))]
        return
    
    ###ROOT GEOMETRY###

    root = tk.Tk()
    root.geometry('900x1070+0+0')
    root.resizable(False, True)
    root.title('MLC Konfiguration - Mittlere 64 Leafs')    
    sliders = [LeafSlider(root,i,zigzag[i]) for i in range(number_of_rendered_leafs)]
    fieldsize = tk.StringVar(root)
    offset = tk.StringVar(root)
    
    ###ROOT BUTTONS###

    button = ttk.Button(root, text="Konfigurieren!", command=lambda:CalculateLeafPositions(number_of_rendered_leafs, leaf_stl_path,\
         number_of_leaf_pairs, MLC_TransZ, SSD, dist_from_xy_plane_to_top_edge, dist_from_z_axis_to_inner_edge, root))
    button.pack()
    button.place(x=535, y=10)
    
    button1 = ttk.Button(root, width = 19, text="Eingabe übernehmen!", command=lambda:set_vals(sliders))
    button1.pack()
    button1.place(x=760, y=10)
    
    button2 = ttk.Button(root, width = 5, text="Wave", command=lambda:choose_preset(root,wave))
    button2.pack()
    button2.place(x=295, y=10)

    button3 = ttk.Button(root, width = 4,  text="Sine", command=lambda:choose_preset(root,sine))
    button3.pack()
    button3.place(x=335, y=10)
    
    button4 = ttk.Button(root, width = 7, text="ZigZag", command=lambda:choose_preset(root,zigzag))
    button4.pack()
    button4.place(x=369, y=10)
    
    button5 = ttk.Button(root, width = 4, text="Diag", command=lambda:choose_preset(root,diag))
    button5.pack()
    button5.place(x=421, y=10)

    button6 = ttk.Button(root, text="cm  - Feld",  width = 9, command=lambda:choose_preset(root))
    button6.pack()
    button6.place(x=45, y=10)
    
    button7 = ttk.Button(root, text="cm Verschiebung", width = 16, command=lambda:move_field(root))
    button7.pack()
    button7.place(x=141, y=10)
    
    ###ENTRY FIELDS###
    
    e1 = tk.Entry(root, width = 3, textvariable = fieldsize)
    e1.pack()
    e1.place(x=19, y=13)
    
    e2 = tk.Entry(root, width = 3, textvariable = offset)
    e2.pack()
    e2.place(x=115, y=13)
    
    root.focus_force()
    root.mainloop()

if __name__ == "__main__":

    try:
        fn = sys.argv[1]                                                                                              #Command line functionality to load a .txt file with 
        load_mlc_data(fn)                                                                                             #position presets. Else start GUI.
        exit()
    except IndexError:   
        main()