import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from typing import Dict, List, Optional, Tuple


def watershed(img: np.ndarray, img_ori: np.ndarray, thresh=0.20, kernel: Tuple = (3, 3), thresh_pre=30, dia_iter=3):
    ''' Excute watershed transform on the original image (img_ori must be a 3-channel image) based on a processed binary image.
    Returns the following images in a dictionary: modified markers generated by the watershed algorithm; segmented orginal image; surely background area; distance transform of the thresholded original image; surely foreground area; unknown area; unmodified markers used to conduct watershed.
    Value of thersh_pre, thresh_dist and kernel must be adjusted according to the processed image.
    '''

    # Generate kernel used for morphological dilation
    kernel = np.ones(kernel, np.uint8)

    # Thresholding to obtain a binary image
    _, img = cv2.threshold(img, thresh_pre, 255, 0, cv2.THRESH_BINARY)
    img = cv2.bitwise_not(img)

    # Obtain surely backgroud area by dilating the image
    sure_bg = cv2.dilate(img, kernel, iterations=dia_iter)

    # Obtain surely foregroud area by thresholding the distance transform of the image
    dist = cv2.distanceTransform(img, cv2.DIST_L2, 5)
    cv2.normalize(dist, dist, 0, 1.0, cv2.NORM_MINMAX)

    _, sure_fg = cv2.threshold(dist, thresh*dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)

    # Unknown area
    unknown = cv2.subtract(sure_bg, sure_fg)

    # Obtain the markers for watershed by conducting a connected component analysis on the surely foreground area
    _, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # Obtain the modifed marker generated by the watershed algorithm and segment the original image
    watershed_markers = []
    watershed_markers = cv2.watershed(img_ori, markers)
    img_ori[markers == -1] = [0, 0, 255]

    return {
        'modified markers': watershed_markers,
        'segmented image': img_ori,
        'sure background': sure_bg,
        'distance transform': dist,
        'sure foreground': sure_fg,
        'unknown': unknown,
        'markers': markers
    }
