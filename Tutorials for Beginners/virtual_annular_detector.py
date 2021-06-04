# Jinseok Ryu
# Electron Microscopy and Spectroscopy Lab.
# Seoul National University
# last update : 20210604
# virtual STEM imaging for 4D-STEM data


# ********************************************************************************
print("Execute Python script in GMS 3")

import DigitalMicrograph as DM
from scipy import optimize
import numpy as np
import sys
sys.argv.extend(['-a', ' '])
import matplotlib.pyplot as plt

print("Libraries have been imported completely")
# ********************************************************************************

# refer to https://scipy-cookbook.readthedocs.io/items/FittingData.html

if ( False == DM.IsScriptOnMainThread() ):
	print( ' MatplotLib scripts require to be run on the main thread.' )
	exit()


def gaussian(height, center_x, center_y, width_x, width_y):
    """Returns a gaussian function with the given parameters"""
    width_x = float(width_x)
    width_y = float(width_y)
    return lambda x,y: height*np.exp(-(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

def moments(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution by calculating its
    moments"""
    total = data.sum()
    X, Y = np.indices(data.shape) # row, col
    x = (X*data).sum()/total # row
    y = (Y*data).sum()/total # col
    col = data[:, int(y)]
    width_x = np.sqrt(np.abs((np.arange(col.size)-y)**2*col).sum()/col.sum()) # row
    row = data[int(x), :]
    width_y = np.sqrt(np.abs((np.arange(row.size)-x)**2*row).sum()/row.sum()) # col
    height = data.max()
    return height, x, y, width_x, width_y

def fitgaussian(data):
    """Returns (height, x, y, width_x, width_y)
    the gaussian parameters of a 2D distribution found by a fit"""
    params = moments(data)
    errorfunction = lambda p: np.ravel(gaussian(*p)(*np.indices(data.shape)) -
                                 data)
    p, success = optimize.leastsq(errorfunction, params)
    return p


def gaussian_center(image, cbox_edge=0):
    y, x = np.indices(image.shape)
    if not cbox_edge:
        center = np.array([(y.max()-y.min())/2.0, (x.max()-x.min())/2.0])
        
    else:
        cbox_outy = int(image.shape[0]/2 - cbox_edge/2)
        cbox_outx = int(image.shape[1]/2 - cbox_edge/2)
        center_box = image[cbox_outy:-cbox_outy, cbox_outx:-cbox_outx]
        fit_params = fitgaussian(center_box)
        (_, center_y, center_x, _, _) = fit_params
        center = [center_y+cbox_outy, center_x+cbox_outx]
        
    return center


def fourd_roll_axis(stack):
    stack = np.rollaxis(np.rollaxis(stack, 2, 0), 3, 1)
    return stack


fd = DM.GetFrontImage()
print(fd)

origin0, scale0, unit0 = fd.GetDimensionCalibration(0, 0)
print(origin0, scale0, unit0)
origin1, scale1, unit1 = fd.GetDimensionCalibration(1, 0)
print(origin1, scale1, unit1)
origin2, scale2, unit2 = fd.GetDimensionCalibration(2, 0)
print(origin2, scale2, unit2)
origin3, scale3, unit3 = fd.GetDimensionCalibration(3, 0)
print(origin3, scale3, unit3)

print("loading 4D-STEM data")
stack_4d_cropped = fourd_roll_axis(fd.GetNumArray())
stack_4d_cropped = np.nan_to_num(stack_4d_cropped)
print(stack_4d_cropped.shape)
print(np.max(stack_4d_cropped))
print(np.min(stack_4d_cropped))
print(np.mean(stack_4d_cropped))

f_shape = stack_4d_cropped.shape

print("maximum-normalizing")
stack_4d_cropped = stack_4d_cropped / np.max(stack_4d_cropped)
print(np.max(stack_4d_cropped))
print(np.min(stack_4d_cropped))
print(np.mean(stack_4d_cropped))

pacbed = np.mean(stack_4d_cropped, axis=(0,1))

check_center = input("Do you want to input the center position manually? (Y / N): ")
if check_center == "Y":
	x_ct = float(input("write the x index of the center: "))
	y_ct = float(input("write the y index of the center: "))
	ct = [y_ct, x_ct]
	
elif check_center=="N":
	#find center position
	q_text = """Select one option for finding the center position.
	1: Gaussian fitting - PACBED
	2: Center of mass - PACBED"""

	q_check = int(input(q_text))

	if q_check == 1:
		cb = int(input("size of the fitting box (data index): "))
		ct = gaussian_center(pacbed, cbox_edge=cb)
		print("center position")
		print(ct)

	elif q_check == 2:
		Y, X = np.indices(pacbed.shape)
		com_y = np.sum(pacbed * Y) / np.sum(pacbed)
		com_x = np.sum(pacbed * X) / np.sum(pacbed)
		ct = [com_y, com_x]
		
		print("center position")
		print(ct)
		
	else:
		print("*"*50)
		print("wrong input !")
		print("*"*50)
		exit()

else:
	print("*"*50)
	print("wrong input !")
	print("*"*50)
	exit()

fig2, ax2 = plt.subplots(1, 1, figsize=(5, 5))
ax2.imshow(pacbed, cmap="gray")
ax2.scatter(ct[1], ct[0], c="red")
ax2.axis("off")

def max_rad(shape, center=None):
    y, x = np.indices(shape)
    if not center:
        center = np.array([(x.max()-x.min())/2.0, (y.max()-y.min())/2.0])
    
    r = np.hypot(y - center[0], x - center[1])
    
    return np.max(r)
    
def radial_indices(shape, radial_range, scale, center=None):
    y, x = np.indices(shape)
    if not center:
        center = np.array([(y.max()-y.min())/2.0, (x.max()-x.min())/2.0])
    
    r = np.hypot(y - center[0], x - center[1]) * scale
    ri = np.ones(r.shape)
    
    if len(np.unique(radial_range)) > 1:
        ri[np.where(r <= radial_range[0])] = 0
        ri[np.where(r > radial_range[1])] = 0
        
    else:
        r = np.round(r)
        ri[np.where(r != round(radial_range[0]))] = 0
    
    return ri


mrad_per_pixel = 1
radii = np.arange(max_rad(f_shape[2:], center=ct)) * mrad_per_pixel
print("maximum angle = %.2f"%(radii[-1]))

check_det = input("Do you want a STEM image for a specific annular region ? (Y or N) ")

if check_det == "Y":
	det_inner_ind = int(input("index of the inner angle (positive integer): "))
	det_outer_ind = int(input("index of the outer angle (positive integer): "))

	det_img = DM.CreateImage(ri.copy())
	det_img.SetName("Detector")
	det_img.SetDimensionCalibration(0, origin2, scale2, unit2, 0)
	det_img.SetDimensionCalibration(1, origin3, scale3, unit3, 0)
	det_img.ShowImage()

	output_img = DM.CreateImage(img_temp.copy())
	output_img.SetName("Annular Dark-filed STEM image")
	output_img.SetDimensionCalibration(0, origin0, scale0, unit0, 0)
	output_img.SetDimensionCalibration(1, origin1, scale1, unit1, 0)
	output_img.ShowImage()
	

elif check_det == "N":
	detector = []
	stem_img = []
	for i in range(len(radii)):
		ri = radial_indices(f_shape[2:], [radii[i]], mrad_per_pixel, center=ct)
		detector.append(ri)
		stem_img.append(np.sum(np.multiply(stack_4d_cropped, ri), axis=(2, 3)))
		
	detector = np.asarray(detector).reshape(1, -1, f_shape[2], f_shape[3])
	print(detector.shape)
	detector = fourd_roll_axis(detector)
	print(detector.shape)
	
	stem_img = np.asarray(stem_img).reshape(1, -1, f_shape[0], f_shape[1])
	print(stem_img.shape)
	stem_img = fourd_roll_axis(stem_img)
	print(stem_img.shape)
	
	det_img = DM.CreateImage(detector.copy())
	det_img.SetName("Virtual Detector")
	det_img.SetDimensionCalibration(2, origin2, scale2, unit2, 0)
	det_img.SetDimensionCalibration(3, origin3, scale3, unit3, 0)
	det_img.ShowImage()
	
	stem = DM.CreateImage(stem_img.copy())
	stem.SetName("STEM image")
	stem.SetDimensionCalibration(2, origin0, scale0, unit0, 0)
	stem.SetDimensionCalibration(3, origin1, scale1, unit1, 0)
	stem.ShowImage()
	

else:
	print("*"*50)
	print("Wrong input !")
	print("*"*50)
	exit()

pacbed_dm = DM.CreateImage(pacbed.copy())
pacbed_dm.SetName("PACBED")
pacbed_dm.SetDimensionCalibration(0, origin2, scale2, unit2, 0)
pacbed_dm.SetDimensionCalibration(1, origin3, scale3, unit3, 0)
pacbed_dm.ShowImage()

plt.show()