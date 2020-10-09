import numpy as np

try:
    import imageio
except ImportError:
    pass

try:
    import py360convert
except ImportError:
    pass


def panorama_to_cubemap(panorama_img, face_size=1024, cube_format="dice"):

    if not isinstance(panorama_img, np.ndarray):
        panorama_img = imageio.imread(panorama_img)

    cubemap_img = py360convert.e2c(
        e_img=panorama_img, face_w=face_size, cube_format=cube_format
    )

    return cubemap_img
