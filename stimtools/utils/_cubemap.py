import numpy as np

try:
    import imageio
except ImportError:
    pass

try:
    import py360convert
except ImportError:
    pass

import stimtools.utils


def panorama_to_cubemap(panorama_img, face_size=1024, panorama_is_srgb=True):

    if not isinstance(panorama_img, np.ndarray):
        panorama_img = imageio.imread(panorama_img)

    if np.max(panorama_img) <= 1.0:
        raise ValueError("Expecting the input image to be in the [0, 255] range")

    panorama_img = panorama_img.astype("float") / 255.0

    if panorama_is_srgb:
        panorama_img = stimtools.utils.srgb_to_linear(img=panorama_img)

    cubemap_img = py360convert.e2c(e_img=panorama_img, face_w=face_size)

    if panorama_is_srgb:
        cubemap_img = stimtools.utils.linear_to_srgb(img=cubemap_img)

    return cubemap_img
