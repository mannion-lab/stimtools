from __future__ import absolute_import, print_function, division

import numpy as np


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

