from __future__ import absolute_import, print_function, division

import numpy as np
import scipy.signal

import stim.utils


def polar_grating(
    size_pix=512,
    n_cycles=10,
    contrast=1.0,
    wave_type="square",
    phase=0.0
):

    half_size = size_pix / 2.0

    (y, x) = np.mgrid[-half_size:half_size, -half_size:half_size]

    (theta, r) = stim.utils.cart_to_pol(x, y)

    theta = np.radians(theta)

    theta = (theta + phase) * n_cycles

    if wave_type == "square":

        img = scipy.signal.square(theta)

    elif wave_type == "quartic":

        img = (
            (np.pi / 2.0) ** -4.0 *
            (np.mod(theta, np.pi) - (np.pi / 2.0)) ** 4 *
            np.sign(np.pi - np.mod(theta, np.pi * 2))
        )

    else:
        raise ValueError("Unknown wave_type")

    img *= contrast

    return img

