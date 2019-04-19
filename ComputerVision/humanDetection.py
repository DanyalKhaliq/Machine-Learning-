#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 12:18:59 2019

@author: danyal
"""

import numpy as np
import cv2

img = cv2.imread('/home/danyal/Projects/OpenCV/images/woman.jpg',1)

upperBody_cascade = cv2.CascadeClassifier('HS.xml')    

arrUpperBody = upperBody_cascade.detectMultiScale(img,1.9, 3)


if arrUpperBody != ():
        for (x,y,w,h) in arrUpperBody:
            cv2.rectangle(img,(x,y),(x+w,y+h),(1,1,1),2)
        print ('body found')

cv2.imshow('image',img)
cv2.waitKey(0)
cv2.destroyAllWindows()