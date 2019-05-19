import numpy as np


def circ_dist(a, b):
    """Computes the circular difference between two angles.

    Parameters
    ----------
    a, b : float
        Angles, in radians.

    """

    return np.angle(np.exp(a * 1j) / np.exp(b * 1j))
