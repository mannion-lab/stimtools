import numpy as np

import imageio

try:
    import py360convert
except ImportError:
    pass


def panorama_to_cubemap(panorama_img, face_size=1024):

    if not isinstance(panorama_img, np.ndarray):
        panorama_img = imageio.imread(panorama_img)

    cubemap_img = py360convert.e2c(e_img=panorama_img, face_w=face_size)

    return cubemap_img
