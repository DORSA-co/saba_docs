import timeit

import cv2
import math
import numpy as np


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get an enhanced version of steel image
#
# arg:
#   img: gray image (np.array shape=(h, w), dtype = np.uint8)
#
# return:
#   imge
#   imge : enhanced image (np.array shape(w, h))
# ______________________________________________________________________________________________________________________________________________
def ImageEnhancement(img):
    # Enhance image for better defect detection
    # Apply GaussianBlur with (5, 5) kernel size
    imge = cv2.GaussianBlur(img, (5, 5), 1.1, 1.1)

    # Smooth image
    imge = ImageSmoothness(imge)

    # Remove small noises
    imge = SmallNoiseRemoval(imge)

    # Detect edges
    imge = EdgeDetection(imge)

    # Normalize image in range [0, 255]
    imge = cv2.normalize(imge, None, 0, 255, cv2.NORM_MINMAX, -1)

    return imge


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get a smoothed version of steel image
#
# arg:
#   img: gray image (np.array shape=(h, w), dtype = np.uint8)
#
# return:
#   imge
#   imge : smoothed image (np.array shape(w, h))
# ______________________________________________________________________________________________________________________________________________
def ImageSmoothness(img):
    # Apply smoothness with following equation:l
    # SmoothedImage = (OriginalImage * 0.5) / (OriginalImage after applying GaussianBlur with (21, 21) kernel size)
    imge = np.divide(np.multiply(img, 0.5), (np.add(cv2.GaussianBlur(img, (21, 21), 3.5, 3.5), math.pow(2, -25))))
    return imge.astype('float32')


# ______________________________________________________________________________________________________________________________________________
# explain:
#   remove small noises from image
#
# arg:
#   img: gray image (np.array shape=(h, w), dtype = np.float64)
#
# return:
#   imge
#   imge : image with small noises removal (np.array shape(w, h))
# ______________________________________________________________________________________________________________________________________________
def SmallNoiseRemoval(img):
    # Apply morphology to remove small noises

    # Define ellipse structuring element with size (3, 3)
    element = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8)

    # Apply first erosion on img
    imge = cv2.erode(img, element, iterations=1)

    # Apply dilation on img
    imge = cv2.dilate(imge, element, iterations=1)

    # Apply second erosion on img
    imge = cv2.erode(imge, element)
    return imge


# ______________________________________________________________________________________________________________________________________________
# explain:
#   detect edges in image
#
# arg:
#   img: gray image (np.array shape=(h, w), dtype = np.float64)
#
# return:
#   imge
#   imge : image with edges detected (np.array shape(w, h))
# ______________________________________________________________________________________________________________________________________________
def EdgeDetection(img):
    # Detect edges with sobel edge detection

    # Find edges in x-axis
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)

    # Find edges in y-axis
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1, ksize=3)

    # Calculates the magnitude 2D vectors
    imge = np.sqrt(gx**2 + gy**2)

    return imge
