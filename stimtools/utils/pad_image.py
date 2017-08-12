from __future__ import absolute_import, print_function, division

import numpy as np


def nearest_pow2(n):
    """Determines the nearest power of two to the value ``n``."""

    return int(np.power(2, np.ceil(np.log(n) / np.log(2))))


def pad_image(img, calc_mask=False, pad_value=0.0, to="pow2"):
    """Pads an image to its nearest power of two.

    Parameters
    ----------
    img: 2D array (or 3D, for colour)
        Image to be padded
    calc_mask: bool, optional
        Whether to also calculate the mask that excludes the padded region.
    pad_value: number, optional
        Value with which to fill the padded region.
    to: str or number, optional
        Dimension to pad the image to. If is 'pow2', the nearest power of 2 is
        calculated and used. If it is 'pow2+', it is one power of 2 more than
        the nearest power of 2.

    Returns
    -------
    (pad_img, mask_img): 2D (or 3D, for colour) array
        Image padded to the desired dimensions, and its mask (2D) if requested.

    """

    if isinstance(to, str):

        if to.startswith("pow2"):

            new_size = nearest_pow2(np.max(img.shape[:2]))

            if to == "pow2+":
                new_size = nearest_pow2(new_size + 1)

            new_size = [new_size] * 2

    else:

        if type(to) not in [list, tuple, np.ndarray]:
            new_size = [to] * 2

        else:
            new_size = to

    new_size = map(int, new_size)

    if img.ndim == 3:
        n_channels = img.shape[-1]
    else:
        n_channels = 1
        img = img[..., np.newaxis]

    pad_img = np.ones((new_size[0], new_size[1], n_channels)) * pad_value

    pad_img[:img.shape[0], :img.shape[1], :] = img

    row_roll_k = int(np.floor((new_size[0] - img.shape[0]) / 2.0))
    col_roll_k = int(np.floor((new_size[1] - img.shape[1]) / 2.0))

    pad_img = np.roll(pad_img, row_roll_k, axis=0)
    pad_img = np.roll(pad_img, col_roll_k, axis=1)

    if n_channels == 1:
        pad_img = pad_img[..., 0]

    if calc_mask:
        mask_img = np.ones(new_size) * -1
        mask_img[:img.shape[0], :img.shape[1]] = 1
        mask_img = np.roll(mask_img, row_roll_k, axis=0)
        mask_img = np.roll(mask_img, col_roll_k, axis=1)

        return (pad_img, mask_img)

    return pad_img
