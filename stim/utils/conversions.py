from __future__ import absolute_import, print_function, division

import numpy as np


def interval_convert(value, old_interval, new_interval):
    """Convert values from one range to another.

    Parameters
    ----------
    value: number
        Value to convert.
    old_interval: two-item list
        Interval from which ``value`` was obtained (min, max)
    new_interval: two-item list
        Desired new interval (min, max)

    Returns
    -------
    new_value: number
        ``value`` transformed to the new interval.

    """

    (old_min, old_max) = old_interval
    old_range = old_max - old_min

    (new_min, new_max) = new_interval
    new_range = new_max - new_min

    new_value = (((value - old_min) * new_range) / old_range) + new_min

    return new_value


def math_to_nav_polar(theta):
    """Convert a polar angle from mathematician's to navigator's polar.

    This converts from mathematician's polar, where 0 is east and increasing
    angles are increasingly anti-clockwise, to navigator's polar, where 0 is
    north and increasing angles are increasingly clockwise.

    PsychoPy coordinates are in navigator's polar.

    """

    is_scalar = np.isscalar(theta)
    is_list = isinstance(theta, list)

    if is_scalar:
        theta = np.array([theta])
    elif is_list:
        theta = np.array(theta)

    theta[theta <= 90.0] = 90.0 - theta[theta <= 90.0]
    theta[theta > 90.0] = 450.0 - theta[theta > 90.0]

    if is_scalar:
        theta = theta[0]
    elif is_list:
        theta = list(theta)

    return theta


def cart_to_pol(x, y):
    """Convert cartesian to mathematician's polar.

    Parameters
    ----------
    x, y : float
        X and Y coordinates

    Returns
    -------
    theta, r : float
        Polar angle and radius. Theta is in degrees.

    """

    r = np.sqrt(x ** 2 + y ** 2)

    theta = np.degrees(np.arctan2(y, x))

    if np.isscalar(theta):
        if theta < 0:
            theta = theta + 360.0
    else:
        theta[theta < 0] = theta[theta < 0] + 360.0

    return (theta, r)


def pol_to_cart(theta, r):
    """Convert mathematician's polar to cartesian.

    Parameters
    ----------
    theta, r: float
        Angle and radius components. Theta is in degrees.

    Returns
    -------
    x, y: float
        X and Y coordinates.

    """

    x = r * np.cos(np.radians(theta))
    y = r * np.sin(np.radians(theta))

    return (x, y)

