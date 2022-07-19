import numpy as np
from .Division import ImageDivision


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get variance of image blocks
#
# arg:
#   img: gray image (np.array shape=(h, w), dtype = np.float64)
#   dim: dimension of blocks
#   ol: overlap between blocks
#
# return:
#   variance
#   variance : variance of image blocks (np.array shape(int(h / (dim - ol)) * int(w / (dim - ol)), ))
# ______________________________________________________________________________________________________________________________________________
def ImageBlockVariance(img, dim, ol):
    # Add ol columns of zero in right side and ol rows of zero in bottom of image for better division
    img = np.pad(img, [(0, ol), (0, ol)], mode='constant')

    # Divide image into blocks with shape (dim, dim) and ol pixel overlap
    blocks = ImageDivision(img, dim, ol)

    # Calculate variance for each block
    variance = VarianceCalculator(blocks, dim)
    return variance.flatten()


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get variance of blocks
#
# arg:
#   blocks: 4-d array of blocks (np.array shape=(nx, ny, dim, dim), dtype = np.float64)
#   dim: dimension of blocks
#
# return:
#   variance
#   variance : variance of each block (np.array shape(nx * ny, ))
# ______________________________________________________________________________________________________________________________________________
def VarianceCalculator(blocks, dim):
    # Compute Variance of img
    return ((((blocks ** 2).sum(axis=3)).sum(axis=2)) / (dim**2)) - ((((blocks.sum(axis=3)).sum(axis=2)) / (dim**2)) ** 2)


# ______________________________________________________________________________________________________________________________________________
# explain:
#   get threshold based on variance for detect defective blocks
#
# arg:
#   variance: variance of blocks (np.array shape(nx * ny, ), dtype = np.float64)
#
# return:
#   v_th
#   v_th : number used in defect detection (integer)
# ______________________________________________________________________________________________________________________________________________
def ThresholdCalculator(variance):
    # Compute threshold based on blocks variance
    sen_v = 0.0125
    max_v = variance.max(initial=0)
    m_v = variance.mean()
    v_th = m_v + (max_v - m_v) * sen_v
    return v_th

