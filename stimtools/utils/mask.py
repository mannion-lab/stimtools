from __future__ import absolute_import, print_function, division

import numpy as np

import stimtools.utils


def polar_mask(
    size_pix,
    outer_extent_norm=1.0,
    inner_extent_norm=0.0,
    sector_centre_deg=0.0,
    sector_central_angle_deg=361.0,
    mask_min=-1.0,
    mask_max=+1.0
):
    """Generates a mask in polar space.

    Parameters
    ----------
    size_pix: int
        Size of the mask, in pixels (both width and height)
    outer_extent_norm, inner_extent_norm: floats
        Inner and outer extent of the mask, in normalised units.
    sector_centre_deg: float
        Centre of the visible 'wedge', in degrees.
    sector_central_angle_deg: float
        Angular width of the visible 'wedge', in degrees.
    mask_min, mask_max: floats
        Minimum and maximum of the returned mask.

    """

    half_size = size_pix / 2.0

    (y, x) = np.mgrid[-half_size:+half_size, -half_size:+half_size]

    (theta, r) = stimtools.utils.cart_to_pol(x, y)

    r = r / half_size

    r_mask = np.logical_and(
        r >= inner_extent_norm,
        r < outer_extent_norm
    )

    theta_dist = np.degrees(
        stimtools.utils.circ_dist(
            np.radians(theta),
            np.radians(sector_centre_deg)
        )
    )

    theta_mask = (np.abs(theta_dist) < (sector_central_angle_deg / 2.0))

    mask = np.logical_and(r_mask, theta_mask).astype("float")

    mask = stimtools.utils.interval_convert(
        value=mask,
        old_interval=[0, 1],
        new_interval=[mask_min, mask_max]
    )

    return mask
