# Jinseok Ryu
# Electron Microscopy and Spectroscopy Lab.
# Seoul National University
# last update : 20210111
# load EMPAD data (.raw)


# ********************************************************************************
print("Execute Python script in GMS 3")

import sys
sys.argv.extend(['-a', ' '])
import tkinter.filedialog as tkf
import DigitalMicrograph as DM
import numpy as np

print("Libraries have been imported completely")
# ********************************************************************************


def load_binary_4D_stack(img_adr, datatype, original_shape, final_shape, log_scale=False):
    stack = np.fromfile(img_adr, dtype=datatype)
    stack = stack.reshape(original_shape)
    print(stack.shape)
    if log_scale:
        stack = np.log(stack[:final_shape[0], :final_shape[1], :final_shape[2], :final_shape[3]])
    else:
        stack = stack[:final_shape[0], :final_shape[1], :final_shape[2], :final_shape[3]]
    
    print(stack.shape) 
    return stack

def fourd_roll_axis(stack):
    stack = np.rollaxis(np.rollaxis(stack, 2, 0), 3, 1)
    return stack


raw_adr = tkf.askopenfilename()
print(raw_adr)
datatype = "float32"

q_text = """Select one option.
1: (256, 256, 128, 128)
2: (128, 128, 128, 128)
3: manual"""

shape_check = eval(input(q_text))
if shape_check == 1:
	o_shape = (256, 256, 130, 128)
	f_shape = (256, 256, 128, 128)
	
elif shape_check == 2:
	o_shape = (128, 128, 130, 128)
	f_shape = (128, 128, 128, 128)
	
elif shape_check == 3:
	sx = int(input("size of the 1st dimension: "))
	sy = int(input("size of the 2nd dimension: "))
	dsx = int(input("size of the 3rd dimension: "))
	dsy = int(input("size of the 4th dimension: "))
	o_shape = (sy, sx, dsy+2, dsx)
	f_shape = (sy, sx, dsy, dsx)

else:
	print("Wrong input !")
	exit()
	
# load a data
stack_4d = load_binary_4D_stack(raw_adr, datatype, o_shape, f_shape, log_scale=False)
print(np.max(stack_4d))
print(np.min(stack_4d))
print(np.mean(stack_4d))
#print(np.median(stack_4d))

additional_check = input("Do you also want to inverse the dimensions? (Y or N): ")
if additional_check == "Y":
	stack_tmp = DM.CreateImage(stack_4d.copy())
	stack_tmp.SetName("dimension-inversed 4D-STEM data")
	stack_tmp.ShowImage()
	
stack_4d = fourd_roll_axis(stack_4d)
stack_dm = DM.CreateImage(stack_4d.copy())
del stack_4d
stack_dm.SetName("4D-STEM data")
stack_dm.ShowImage()