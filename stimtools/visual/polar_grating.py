from __future__ import absolute_import, print_function, division

import numpy as np
import scipy.signal

import stim.utils


def polar_grating(
    size_pix=512,
    n_cycles=10,
    amplitude=1.0,
    wave_type="square",
    phase_radians=0.0
):
    """Generates a polar grating array.

    Parameters
    ----------
    size_pix: int, optional
        Size of the array (both width and height)
    n_cycles: number, optional
        Number of grating cycles over the full polar angle range.
    amplitude: number, optional
        Amplitude of the grating.
    wave_type: string, {"square", "quartic"}
        Wave function, either a square wave or a quartic.
    phase_radians: float, [0, 2pi]
        Grating phase, in radians.

    Returns
    -------
    img: (size_pix, size_pix) array of floats
        Grating image in the range -1:1.

    """

    half_size = size_pix / 2.0

    (y, x) = np.mgrid[-half_size:half_size, -half_size:half_size]

    (theta, _) = stim.utils.cart_to_pol(x, y)

    theta = np.radians(theta)

    theta = (theta + phase_radians) * n_cycles

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

    img *= amplitude

    return img
