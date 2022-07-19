import math
import timeit
import cv2
from skimage.filters import threshold_yen
import numpy as np
# calibrationCal\Preprocessing.py
from .Preprocessing import ImageEnhancement
from .Variance import ImageBlockVariance, ThresholdCalculator
from .Noise import NoiseDetection

DEFECT_BLOCKSIZE = {'Small': 21, 'Medium': 32, 'Large': 54}
NOISE_BLOCKSIZE = {'Small': 7, 'Medium': 8, 'Large': 9}

OVERLAP = 10


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get defective regions and heatmap of image
#
# arg:
#   img: steel image (np.array shape=(h, w, 3), dtype = np.uint8)
#
# return:
#   res, hm
#   res: original image with rectangle around  defective regions (np.array shape=(h, w, 3))
#   hm: heatmap of defects in image
# ______________________________________________________________________________________________________________________________________________
def SSI(img, block_size='Small', defect_th=0, noise_th=7, noise=True, heatmap=False):
    # Resize image

    img=cv2.imread(img)

    img = cv2.resize(img, (978, 528))

    # Crop 10px from left side
    img = img[:, 10:]

    # Convert image to grayscale format
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Divide image into 4 image with shape (132, 968, 3)
    imgs = [gray[0:132, :], gray[132:264, :], gray[264:396, :], gray[396:528, :]]
    t = list(map(FindDefectiveBlocks, imgs, [block_size]*4, [defect_th]*4, [noise_th]*4, [noise] * 4, [heatmap] * 4))

    df = np.concatenate([t[0]['mask'], t[1]['mask'], t[2]['mask'], t[3]['mask']])
    if heatmap:
        hm = np.concatenate([t[0]['heatmap'], t[1]['heatmap'], t[2]['heatmap'], t[3]['heatmap']])

    # Draw rectangle around defective regions
    res = img.copy()
    contours = cv2.findContours(df, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

    # df = np.zeros_like(df)
    for cntr in contours:
        x, y, w, h = cv2.boundingRect(cntr)
        x -= 5
        y -= 5
        h += 10
        w += 10
        cv2.rectangle(res, (x, y), (x + w, y + h), (205, 175, 33), 2)

    # Improve heatmap based on defect mask
    if heatmap:
        hm[:, :, 0] *= (df / 255).astype('uint8')
        hm[:, :, 1] *= (df / 255).astype('uint8')
        hm[:, :, 2] *= (df / 255).astype('uint8')
        return res, hm
    else:
        return res


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get defective mask and heatmap of image
#
# arg:
#   img: steel image (np.array shape=(132, 968, 3), dtype = np.uint8)
#
# return:
#   {'mask': defectMask, 'heatmap': heatmap} (dictionary)
#   defectiveMask: mask of defective blocks (np.array shape=(132, 968))
#   heatmap: heatmap of image (np.array shape=(132, 968, 3))
# ______________________________________________________________________________________________________________________________________________
def FindDefectiveBlocks(gray, block_size='small', defect_th=0, noise_th=7, noise=True, heatmap=False):
    # Enhance image for better defect detection
    imge = ImageEnhancement(gray)
    dim = DEFECT_BLOCKSIZE[block_size]
    ndim = NOISE_BLOCKSIZE[block_size]

    # Find defective blocks

    # Find variance of each block
    variance = ImageBlockVariance(imge, dim, OVERLAP)

    # Compute mean of blocks variance
    m_v = variance.mean()

    # Compute threshold v_th for image
    v_th = ThresholdCalculator(variance)

    # Find number of blocks in x-axis and y-axis
    h, w = imge.shape
    ny = int(w / (dim - OVERLAP))

    # Detect defective blocks based on variance and threshold
    # Decide about defect threshold and noise threshold based on average variance of blocks
    defectiveBlocks = 0
    th = -1
    if m_v >= 300:
        defectiveBlocks = np.where(variance > (4+defect_th) * v_th)[0]

    elif 300 > m_v >= 200:
        defectiveBlocks = np.where(variance > (3+defect_th) * v_th)[0]
        if noise:
            th = noise_th*5

    elif 200 > m_v >= 100:
        defectiveBlocks = np.where(variance > (2+defect_th) * v_th)[0]
        if noise:
            th = (noise_th+1)*5

    elif m_v < 100:
        defectiveBlocks = np.where(variance > (1.5+defect_th) * v_th)[0]
        if noise:
            th = (noise_th+1)*5 + 2

    # Find noisy blocks based on defined thresholds
    defectMask = np.zeros_like(imge, dtype='uint8')
    for c in defectiveBlocks:
        d = math.floor(c / ny) * (dim - OVERLAP)
        m = (c % ny) * (dim - OVERLAP)

        if th < 0:
            defectMask[d:d + dim, m:m + dim] = 255

        elif NoiseDetection(imge[d:d + dim, m:m + dim], dim, ndim) >= th:
            defectMask[d:d + dim, m:m + dim] = 255
    # Create heatmap of gray image
    if heatmap:
        heatmap = CreateHeatmap(gray, imge)

        # Return heatmap and mask of defects
        return {'mask': defectMask, 'heatmap': heatmap}
    else:
        return {'mask': defectMask}


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get heatmap of image
#
# arg:
#   img: steel image after enhancement (np.array shape=(h, w), dtype = np.float64)
#   gray: gray scale steel image (np.array shape=(h, w), dtype = np.uint8)
#
# return:
#   heatmap
#   heatmap: heatmap of image (np.array shape=(h, w, 3))
# ______________________________________________________________________________________________________________________________________________
def CreateHeatmap(gray, img):
    # Image thresholding based on yen thresholding
    th = threshold_yen(img)
    imgt = cv2.threshold(img.astype('uint8'), th, 1, cv2.THRESH_BINARY, None)[1]

    # Normalize binary image multiply by gray image between [0, 255]
    t = cv2.normalize((imgt * gray).astype('uint8'), None, 0, 255, cv2.NORM_MINMAX, -1, None)

    # Create heatmap of image
    heatmap = cv2.applyColorMap(255 - t, cv2.COLORMAP_AUTUMN)

    # Multiply heatmap with binary image to remove background
    heatmap[:, :, 0] *= imgt.astype('uint8')
    heatmap[:, :, 1] *= imgt.astype('uint8')
    heatmap[:, :, 2] *= imgt.astype('uint8')

    return heatmap
