from __future__ import absolute_import, print_function, division

import numpy as np

import stim.utils


def circ_mask(
    size_pix,
    outer_extent_norm=1.0,
    inner_extent_norm=0.0,
    mask_min=-1.0,
    mask_max=+1.0
):

    half_size = size_pix / 2.0

    (y, x) = np.mgrid[-half_size:+half_size, -half_size:+half_size]

    (_, r) = stim.utils.cart_to_pol(x, y)

    r = r / half_size

    mask = np.logical_and(
        r >= inner_extent_norm,
        r < outer_extent_norm
    ).astype("float")

    mask = stim.utils.interval_convert(
        value=mask,
        old_interval=[0, 1],
        new_interval=[mask_min, mask_max]
    )

    return mask
