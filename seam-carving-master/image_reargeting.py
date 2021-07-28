import cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import convolve
from tqdm import trange

def imshow(img):
    if (len(img.shape) == 2) :
        plt.imshow(img)
        plt.show()
        return
    b,g,r = cv2.split(img) 
    img_rgb = cv2.merge([r,g,b]) 
    plt.imshow(img_rgb)
    plt.show()


img = cv2.imread('./in/images/image.jpg')
imshow(img)
img.shape

width = 900
height = img.shape[0]
crop = img[:height, :width]
imshow(crop)

width = 900
height = img.shape[0]
crop = img[:height, (img.shape[1] - width) // 2 : (img.shape[1] + width) // 2]
imshow(crop)

def cal_energy(img):
    filter_du = np.array([
        [1.0, 2.0, 1.0],
        [0.0, 0.0, 0.0],
        [-1.0, -2.0, -1.0],
    ])

    filter_du = np.stack([filter_du] * 3, axis=2)

    filter_dv = np.array([
        [1.0, 0.0, -1.0],
        [2.0, 0.0, -2.0],
        [1.0, 0.0, -1.0],
    ])

    filter_dv = np.stack([filter_dv] * 3, axis=2)

    img = img.astype('float32')

    convolved = np.absolute(convolve(img, filter_du)) + np.absolute(convolve(img, filter_dv))

    energy_map = convolved.sum(axis=2)
    
    return energy_map

energy_map = cal_energy(img)
print(energy_map.shape)
imshow(energy_map)



def minimum_seam(img):
    r, c, _ = img.shape
    energy_map = cal_energy(img)

    M = energy_map.copy()
    backtrack = np.zeros_like(M, dtype=np.int)

    for i in range(1, r):
        for j in range(c):
            if j == 0:
                idx = np.argmin(M[i - 1, j:j + 2])
                backtrack[i, j] = idx + j
                min_energy = M[i - 1, idx + j]
            else:
                idx = np.argmin(M[i - 1, j - 1:j + 2])
                backtrack[i, j] = idx + j - 1
                min_energy = M[i - 1, idx + j - 1]

            M[i, j] += min_energy
    return M, backtrack
M, backtrack = minimum_seam(img)
imshow(M)

def carve_column(img):
    r, c, _ = img.shape

    M, backtrack = minimum_seam(img)

    mask = np.ones((r, c), dtype=np.bool)

    j = np.argmin(M[-1])

    for i in reversed(range(r)):
        mask[i, j] = False
        j = backtrack[i, j]

    mask = np.stack([mask] * 3, axis=2)

    img = img[mask].reshape((r, c - 1, 3))

    return img
for i in trange(100):
    one = carve_column(img)
imshow(one)


def crop_c(img, scale_c):
    r, c, _ = img.shape
    new_c = int(scale_c * c)

    for i in trange(c - new_c):
        img = carve_column(img)

    return img
crop = crop_c(img, 0.8)
imshow(crop)

def crop_r(img, scale_r):
    img = np.rot90(img, 1, (0, 1))
    img = crop_c(img, scale_r)
    img = np.rot90(img, 3, (0, 1))
    return img
crop = crop_r(img, 0.8)
imshow(crop)