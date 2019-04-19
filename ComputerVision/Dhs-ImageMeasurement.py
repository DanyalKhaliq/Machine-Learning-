#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 14:23:59 2019

@author: danyal
"""

import sys
import cv2
import numpy
from scipy.ndimage import label

def segment_on_dt(a, img):
    border = cv2.dilate(img, None, iterations=5)
    border = border - cv2.erode(border, None)

    dt = cv2.distanceTransform(img, 2, 3)
    dt = ((dt - dt.min()) / (dt.max() - dt.min()) * 255).astype(numpy.uint8)
    _, dt = cv2.threshold(dt, 180, 255, cv2.THRESH_BINARY)
    lbl, ncc = label(dt)
    lbl = lbl * (255 / (ncc + 1))
    # Completing the markers now. 
    lbl[border == 255] = 255

    lbl = lbl.astype(numpy.int32)
    cv2.watershed(a, lbl)

    lbl[lbl == -1] = 0
    lbl = lbl.astype(numpy.uint8)
    return 255 - lbl


img = cv2.imread('/home/danyal/Projects/OpenCV/images/woman.jpg')
img = cv2.resize(img, (450, 280))

# Pre-processing.
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)    
_, img_bin = cv2.threshold(img_gray, 0, 255,
        cv2.THRESH_OTSU)
img_bin = cv2.morphologyEx(img_bin, cv2.MORPH_OPEN,
        numpy.ones((3, 3), dtype=int))

result = segment_on_dt(img, img_bin)
#result[result == 0] = 255
#result[result == 128] = 0

#can = cv2.Canny(result, 10, 300)
#cv2.imshow('Canny', can)


# Countours Found
contours, hierarchy = cv2.findContours(result,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(img, contours, 1, (0 ,255, 0), 3)
c = max(contours, key = cv2.contourArea)
x,y,w,h = cv2.boundingRect(contours[1])
print(x,y,w,h)
    # draw the book contour (in green)
cv2.rectangle(img,(x,y),(x+w,y+h),(150,0,0),2)
#cv2.imshow('result', img)

crop_img = img[y:y+h, x:x+w] #img[y:y+h, x:x+w]
#cv2.imshow('crop',crop_img)

imgheight = crop_img.shape[0] #h
imgwidth = crop_img.shape[1] #w

y1 = 0
M = imgheight//9
N = imgwidth//2

for yy in range(0,imgheight,M):
    for xx in range(0, imgwidth, N):
        y1 = yy + M
        x1 = xx + N
        tiles = crop_img[yy:yy+M,xx:xx+N]

        cv2.rectangle(crop_img, (xx, yy), (x1, y1), (150, 150, 0))
        cv2.imwrite("save/" + str(xx) + '_' + str(yy)+".png",tiles)

#cv2.imwrite("asas.png",crop_img)
cv2.imshow('grid',crop_img)


#Extreme Points
#cnt = contours[2]
#leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
#rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
#topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
#bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])

#img = img.astype('uint8')
#blur = cv.GaussianBlur(img,(5,5),0)
#ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY | cv.THRESH_OTSU)
#image = np.invert(th3)
#cv.imshow('image_out', image)

cv2.waitKey(0)
cv2.destroyAllWindows()