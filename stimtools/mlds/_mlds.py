

import itertools

import numpy as np
import scipy.stats


def gen_items(n_levels, n_per_trial):
    """Generate the item indices for an MLDS experiment.

    Parameters
    ----------
    n_levels: int
        Number of stimulus 'levels' (parameter `p`).
    n_per_trial: int
        Number of stimuli shown on a given trial (e.g. quads is 4, triads is 3)

    Returns
    -------
    i_items: numpy array of ints
        Stimulus indices for each trial. These are 'non-overlapping', in the
        sense that 'a < b < c', where (a, b, c) = i_items[i, :].

    """

    i_items = list(itertools.combinations(range(n_levels), n_per_trial))

    return np.array(i_items)


def prob(levels, sigma):
    """Returns the probablity of responding that the second interval difference
    was larger.

    Parameters
    ----------
    levels: numpy array of floats
        Internal stimulus representation levels. Can be of length 3 (triads) or
        4 (quads). Can also be 2D, with the second axis being multiple trials.
    sigma: float
        Noise level.

    Returns
    -------
    prob: float or numpy array of floats
        Probability of responding that the second interval difference was
        larger.

    """

    levels = np.array(levels)

    if levels.ndim == 1:
        levels = levels[:, np.newaxis]

    # triad
    if levels.shape[0] == 3:
        (a, b, c) = levels
        mu = np.abs(c - b) - np.abs(b - a)

    elif len(levels) == 4:
        (a, b, c, d) = levels
        mu = np.abs(d - c) - np.abs(b - a)

    p = 1.0 - scipy.stats.distributions.norm.cdf(x=0.0, loc=mu, scale=sigma)

    return p
