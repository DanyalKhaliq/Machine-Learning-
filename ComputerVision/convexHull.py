#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 16 17:12:24 2019

@author: danyal
"""

from __future__ import print_function
import cv2 as cv
import numpy as np
import argparse
import random as rng
from scipy.ndimage import label
rng.seed(12345)

def segment_on_dt(a, img):
    border = cv.dilate(img, None, iterations=5)
    border = border - cv.erode(border, None)

    dt = cv.distanceTransform(img, 2, 3)
    dt = ((dt - dt.min()) / (dt.max() - dt.min()) * 255).astype(np.uint8)
    _, dt = cv.threshold(dt, 180, 255, cv.THRESH_BINARY)
    lbl, ncc = label(dt)
    lbl = lbl * (255 / (ncc + 1))
    # Completing the markers now. 
    lbl[border == 255] = 255

    lbl = lbl.astype(np.int32)
    cv.watershed(a, lbl)

    lbl[lbl == -1] = 0
    lbl = lbl.astype(np.uint8)
    return 255 - lbl

def thresh_callback(val):
    threshold = val
    # Detect edges using Canny
    #canny_output = cv.Canny(src_gray, threshold, threshold * 2)
    canny_output = src_gray
    # Find contours
    contours, _ = cv.findContours(src_gray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
    # Find the convex hull object for each contour
    hull_list = []
    for i in range(len(contours)):
        hull = cv.convexHull(contours[i])
        hull_list.append(hull)
    # Draw contours + hull results
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    for i in range(len(contours)):
        color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
        cv.drawContours(drawing, contours, i, (255,0,255))
        cv.drawContours(drawing, hull_list, i, color)
    
    #Find Biggest Contour : TODO
    hull = cv.convexHull(contours[2],returnPoints = False)
    defects = cv.convexityDefects(contours[2],hull)
    x,y,w,h = cv.boundingRect(contours[2])
    print(x,y,w,h)
    cnt = contours[2]
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        print(start,end,far)
        cv.line(drawing,start,end,[0,255,0],2)
        cv.circle(drawing,far,3,[0,0,255],-1)
        cv.rectangle(drawing,(x,y),(x+w,y+h),(255,255,255),2)

    cv.imshow('img',drawing)
    # Show in a window
    #cv.imshow('Contours', drawing)
    return hull_list , contours , h , defects

src = cv.imread('/home/danyal/Projects/OpenCV/images/woman.jpg')
if src is None:
    print('Could not open or find the image:')
    exit(0)
# Convert image to gray and blur it
src_gray = cv.cvtColor(src, cv.COLOR_BGR2GRAY)    
_, img_bin = cv.threshold(src_gray, 0, 255,
        cv.THRESH_OTSU)
src_gray = segment_on_dt(src, img_bin)
src_gray[src_gray == 0] = 255
src_gray[src_gray == 128] = 0

# Create Window
source_window = 'Source'
cv.namedWindow(source_window)
cv.imshow(source_window, src)
max_thresh = 255
thresh = 100 # initial threshold
cv.createTrackbar('Canny thresh:', source_window, thresh, max_thresh, thresh_callback)
gHull,gContours,height,gDefects = thresh_callback(thresh)

heightInCm = 162
CmPerPixel =  height / heightInCm

cv.waitKey(0)
cv.destroyAllWindows()