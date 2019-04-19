#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 16:26:47 2019

@author: danyal
"""

import numpy as np
import cv2 as cv
base_dir = "/home/danyal/Projects/OpenCV/"
 
img = cv.imread(base_dir + 'images/woman.jpg',1)
img = np.array(img, dtype=np.uint8)
imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(imgray, 200, 255, 0)
contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
img = cv.drawContours(img, contours, 2, (0,255,0), 3)
cv.imshow('result',  img)


cv.waitKey(0)
cv.destroyAllWindows()