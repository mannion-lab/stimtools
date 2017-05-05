from __future__ import absolute_import, print_function, division

import distutils.version

import numpy as np


def nearest_pow2(n):
    """Determines the nearest power of two to the value ``n``."""

    return np.power(2, np.ceil(np.log(n) / np.log(2)))


def pad_image(img, calc_mask=False, pad_value=0, to="pow2"):
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

    if isinstance(pad_value, float):

        np_version = distutils.version.StrictVersion(np.version.version)

        necc_version = distutils.version.StrictVersion("1.10")

        if np_version < necc_version:

            raise ValueError(
                "For this version of numpy (< 1.10), only integers are " +
                "accepted for `pad_value'"
            )

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

    img_size = img.shape[:2]

    new_size = [int(new_dim_size) for new_dim_size in new_size]

    if img.ndim == 3:
        n_channels = img.shape[-1]
    else:
        n_channels = 1
        img = img[..., np.newaxis]

    pad_amounts = []

    # iterate over the spatial dimensions
    for i_dim in range(2):

        first_offset = int((new_size[i_dim] - img_size[i_dim]) / 2.0)
        second_offset = new_size[i_dim] - img_size[i_dim] - first_offset

        pad_amounts.append([first_offset, second_offset])

    # don't want to pad the colour channels
    pad_amounts += [[0, 0]]

    pad_img = np.pad(
        array=img,
        pad_width=pad_amounts,
        mode="constant",
        constant_values=pad_value
    )

    if n_channels == 1:
        pad_img = pad_img[..., 0]

    if calc_mask:

        mask = np.ones(img_size)

        pad_mask = np.pad(
            array=mask,
            pad_width=pad_amounts[:2],
            mode="constant",
            constant_values=-1
        )

        return (pad_img, pad_mask)

    return pad_img
