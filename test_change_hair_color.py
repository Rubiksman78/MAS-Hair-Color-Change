import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import re
import time

#list files in folder 'mod_assets/monika/h'
files = os.listdir('../mod_assets/monika/h')

#choose file to edit with a gui which display also the image
root = tk.Tk()
root.withdraw()
file = filedialog.askopenfilename(initialdir = '../mod_assets/monika/h', title = 'Select file', filetypes = (('png files', '*.png'), ('all files', '*.*')))
root.destroy()

#remove -back.png or -front.png or -back(i).png or -front(i).png
file = re.sub(r'(-back|-front)(\(\d+\))?\.png$', '', file)
file_front = file + '-front.png'
file_back = file + '-back.png'

print(file_front, file_back)
#read image
im_front = cv2.imread(file_front, cv2.IMREAD_UNCHANGED)
im_back = cv2.imread(file_back, cv2.IMREAD_UNCHANGED)

im_backup_front = im_front.copy()
im_backup_back = im_back.copy()

#mask is im_front with values >0 and where mean is < 180
# mask = np.all(im_front > 0, axis=2) & (np.mean(im_front, axis=2) < 180)
#keep only points where all channels are > 0 and not [37, 150, 190] with a tolerance of 5
#mask = np.all(im_front > 0, axis=2) & (np.abs(im_front[:,:,0] - 125) > 0) & (np.abs(im_front[:,:,1] - 118) > 0) & (np.abs(im_front[:,:,2] - 190) > 0)
# mask = np.all(im_front > 0, axis=2) & (im_front[:,:,:3] != [125, 118, 190]).all(axis=2)

mask_front = im_front[:,:,3] > 0
inverse_mask_front = im_front[:,:,3] == 0
color_mask_front = np.ones_like(im_front, dtype=np.float32)

mask_back = im_back[:,:,3] > 0
inverse_mask_back = im_back[:,:,3] == 0
color_mask_back = np.ones_like(im_back, dtype=np.float32)

#put all the rest to black
color_mask_front[~mask_front] = [0, 0, 0, 0]
color_mask_back[~mask_back] = [0, 0, 0, 0]
def nothing(x):
    pass

# Create a black image, a window
cv2.namedWindow('hair_color')

# Resize window
cv2.resizeWindow('hair_color', 700, 300)

im_front[~mask_front] = [0, 0, 0, 0]
im_copy_front = im_front.copy()
#im_copy_front = im_copy_front.astype(np.float32)/255

im_back[~mask_back] = [0, 0, 0, 0]
im_copy_back = im_back.copy()
#im_copy_back = im_copy_back.astype(np.float32)/255

# # create trackbars for color change
# cv2.createTrackbar('R','hair_color',0,100,nothing)
# cv2.createTrackbar('G','hair_color',0,100,nothing)
# cv2.createTrackbar('B','hair_color',0,100,nothing)

# while(1):
#     # Get current positions of four trackbars
#     r = cv2.getTrackbarPos('R','hair_color')
#     g = cv2.getTrackbarPos('G','hair_color')
#     b = cv2.getTrackbarPos('B','hair_color')

#     r_percent = r/100 
#     g_percent = g/100 
#     b_percent = b/100 

#     # Apply color change
#     color_mask_front[mask_front] = [b_percent, g_percent, r_percent, 1]

#     color_mask_back[mask_back] = [b_percent, g_percent, r_percent, 1]

#     # Apply color mask
#     im_front = im_copy_front * color_mask_front
#     im_back = im_copy_back * color_mask_back
#     cv2.putText(im_front, 'Press ESC to exit and save changes', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0.9, 0.9, 0.9), 2, cv2.LINE_AA)

#     # Display the front and back image side by side
#     im = np.concatenate((im_front, im_back), axis=1)
#     cv2.imshow('hair_color', cv2.resize(im,(700,300)))
   
#     k = cv2.waitKey(1) & 0xFF
#     if k == 27:
#         break

# cv2.destroyAllWindows()

#convert to hsv and change hue value
hsv_front = cv2.cvtColor(im_front, cv2.COLOR_BGR2HSV)
hsv_back = cv2.cvtColor(im_back, cv2.COLOR_BGR2HSV)

cv2.createTrackbar('H','hair_color',0,360,nothing)
cv2.createTrackbar('S','hair_color',0,255,nothing)
cv2.createTrackbar('V','hair_color',0,255,nothing)

bit_mask_front = np.stack((mask_front,)*3, axis=-1)
bit_mask_back = np.stack((mask_back,)*3, axis=-1)

bit_inverse_mask_front = np.stack((inverse_mask_front,)*3, axis=-1)
bit_inverse_mask_back = np.stack((inverse_mask_back,)*3, axis=-1)
print(np.sum(bit_mask_front==True),np.sum(bit_mask_front==False))

h_front, s_front, v_front = cv2.split(hsv_front)
h_back, s_back, v_back = cv2.split(hsv_back)

while(1):
    # Get current positions of four trackbars
    h = cv2.getTrackbarPos('H','hair_color')
    s = cv2.getTrackbarPos('S','hair_color')
    v = cv2.getTrackbarPos('V','hair_color')

    # Add color change to the initial hue value
    # hsv_front[mask_front][:,0] = np.mod(hsv_front_copy[mask_front][:,0] + h, 180)
    # hsv_back[mask_back][:,0] = np.mod(hsv_back_copy[mask_back][:,0] + h, 180)

    h_front_new = np.mod(h_front + h, 180).astype(np.uint8)
    h_back_new = np.mod(h_back + h, 180).astype(np.uint8)

    s_front_new = np.mod(s_front + s, 255).astype(np.uint8)
    s_back_new = np.mod(s_back + s, 255).astype(np.uint8)

    v_front_new = np.mod(v_front + v, 255).astype(np.uint8)
    v_back_new = np.mod(v_back + v, 255).astype(np.uint8)

    hsv_front = cv2.merge((h_front_new, s_front_new, v_front_new))
    hsv_back = cv2.merge((h_back_new, s_back_new, v_back_new))

    bgr_front = cv2.cvtColor(hsv_front, cv2.COLOR_HSV2BGR)
    bgr_back = cv2.cvtColor(hsv_back, cv2.COLOR_HSV2BGR)

    # # Apply color mask
    # im_front = cv2.bitwise_or(cv2.bitwise_and(im_copy_front[:,:,:3], im_copy_front[:,:,:3], mask=bit_mask_front), cv2.bitwise_and(bgr_front, bgr_front, mask=bit_inverse_mask_front))
    # im_back = cv2.bitwise_or(cv2.bitwise_and(im_copy_back[:,:,:3], im_copy_back[:,:,:3], mask=bit_mask_back), cv2.bitwise_and(bgr_back, bgr_back, mask=bit_inverse_mask_back))
    im_front[:,:,:3] = np.where(bit_mask_front, bgr_front, im_copy_front[:,:,:3])
    im_back[:,:,:3] = np.where(bit_mask_back, bgr_back, im_copy_back[:,:,:3])

    cv2.putText(im_front, 'Press ESC to exit and save changes', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0.9, 0.9, 0.9), 2, cv2.LINE_AA)

    # Display the front and back image side by side
    im = np.concatenate((im_front, im_back), axis=1)
    cv2.imshow('hair_color', cv2.resize(im,(700,300)))
   
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
#Ask if the user wants to save the changes
root = tk.Tk()
root.withdraw()
answer = messagebox.askyesno("Save changes", "Do you want to save the changes?")
root.destroy()

print(answer)
if answer == False:
    im_front = im_backup_front/255
    im_back = im_backup_back/255

#save image and backup
cv2.imwrite(file_back, im_back*255)
cv2.imwrite(file_front, im_front*255)
if not os.path.isfile(file + '-back-backup.png') and not os.path.isfile(file + '-front-backup.png') and answer == True:
    cv2.imwrite(file + '-back-backup.png', im_backup_back)
    cv2.imwrite(file + '-front-backup.png', im_backup_front)

print("Done!")
time.sleep(3)