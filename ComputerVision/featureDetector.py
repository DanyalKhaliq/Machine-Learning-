#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 16:13:32 2019

@author: danyal
"""

import cv2 as cv
import numpy as np

img = cv.imread('/home/danyal/Projects/OpenCV/images/woman.jpg',1)


gray = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV+cv.THRESH_OTSU)

contours, hierarchy = cv.findContours(thresh,cv.RETR_TREE,cv.CHAIN_APPROX_SIMPLE)
thresh = cv.drawContours(img, contours, -1, (0,255,0), 3)
cv.imshow('image_out', thresh)
cv.waitKey(0)
cv.destroyAllWindows()
