import sys
sys.argv.extend(['-a', ' '])
import DigitalMicrograph as DM
import numpy as np
import tifffile
import tkinter.filedialog as tkf

def threed_roll_axis(img):
    stack = np.rollaxis(img, 2, 0)
    return stack
    
def fourd_roll_axis(stack):
    stack = np.rollaxis(np.rollaxis(stack, 2, 0), 3, 1)
    return stack

img_adr = tkf.askopenfilenames()
print("number of the selected files: ", len(img_adr))
print(*img_adr, sep="\n")


for i in range(len(img_adr)):
    adr = img_adr[i]
    if adr[-3:] == "tif" or adr[-4:]=="tiff":
        data = tifffile.imread(adr)
        print(data.shape)

    else:
        print("wrong input !")
        exit()


    if len(data.shape) == 4:
        data = fourd_roll_axis(data)

    elif len(data.shape) == 3:
        data = threed_roll_axis(data)


    data_dm = DM.CreateImage(data.copy())
    data_dm.SetName("tif file loaded_%02d"%(i+1))
    data_dm.ShowImage()