import numpy as np
from .Division import ImageDivision


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get a number for noise detection
#
# arg:
#   img: gray image (np.array shape=(h, w), dtype = np.float64)
#   dim: dimension of blocks
#
# return:
#   num
#   num : number used in noise detection (integer)
# ______________________________________________________________________________________________________________________________________________
def NoiseDetection(img, dim, ndim):
    # Divide img into (dim, dim) sub-blocks
    if img.shape[0] != dim:
        img = np.pad(img, [(0, dim - img.shape[0]), (0, 0)], mode='constant')
    if img.shape[1] != dim:
        img = np.pad(img, [(0, 0), (0, dim - img.shape[1])], mode='constant')

    # blocks = np.swapaxes(img.reshape(4, 8, 4, -1), 1, 2)

    blocks = ImageDivision(img, ndim, 0)

    # Find maximum of each sub-block and save in 1-d array x
    x = ((blocks.max(axis=3)).max(axis=2)).flatten()

    # For each coordinate i in x compute:
    # abs(x[i] - x[i - 1]) + abs(x[i] - x[i + 1])
    # and save in 1-d array y
    y = np.zeros(x.shape[0], dtype=np.float64)
    y[0] = abs(x[1] - x[0])
    y[x.shape[0] - 1] = abs(x[x.shape[0] - 1] - x[x.shape[0] - 2])
    for i in range(1, x.shape[0] - 1): y[i] = abs(x[i] - x[i - 1]) + abs(x[i] - x[i + 1])

    # Find standard deviation of y
    num = round(y.std())
    return num
