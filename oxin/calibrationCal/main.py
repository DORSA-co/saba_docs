import cv2
import os
import timeit
from .SteelSurfaceInspection import SSI
from .Division import ImageDivision

HEATMAP = False
NOISE = True

if __name__ == '__main__':
    # Define folder of images
    imgFolder = '/home/reyhane/Desktop/Images2'

    # List files in folder
    imgFiles = os.listdir(imgFolder)
    imgs = []

    for file in imgFiles:
        # Read images
        imgs.append(cv2.imread(os.path.join(imgFolder, file)))

    start = timeit.default_timer()
    for img in imgs:
        # Start timer
        s = timeit.default_timer()

        # Call SSI function to find defects in image
        if HEATMAP:
            res, hm = SSI(img, 'Medium', 0, 7, NOISE, HEATMAP)
        else:
            res = SSI(img, 'Medium', 0, 7, NOISE, HEATMAP)

        # Stop timer
        end = timeit.default_timer()
        #
        # # Print time spent
        print((end - s) * 1000)
        #
        # Show original image
        cv2.imshow('Original', cv2.resize(img, (968, 528)))

        # Show result image
        cv2.imshow('Result', res.astype('uint8'))

        # Show heatmap
        if HEATMAP:
            cv2.imshow('heatmap', hm)

        cv2.waitKey(0)
    end = timeit.default_timer()
    print((end - start))
