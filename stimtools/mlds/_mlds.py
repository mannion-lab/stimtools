

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

    (mu, *_) = get_delta(levels=levels)

    p = 1.0 - scipy.stats.distributions.norm.cdf(x=0.0, loc=mu, scale=sigma)

    return p


def get_delta(levels):

    levels = np.array(levels)

    if levels.ndim == 1:
        levels = levels[:, np.newaxis]

    (n_levels, *_) = levels.shape

    # triad
    if n_levels == 3:
        (a, b, d) = levels
        c = b
    elif n_levels == 4:
        (a, b, c, d) = levels
    else:
        raise ValueError(
            f"Unexpected levels length ({n_levels:d})"
        )

    delta_1 = np.abs(d - c)
    delta_2 = np.abs(b - a)

    delta = delta_1 - delta_2

    return (delta, delta_1, delta_2)


def prob_scaled(levels, sigma):

    sigma_scaled = sigma * np.sqrt(np.mean(levels ** 2))

    p = prob(levels=levels, sigma=sigma_scaled)

    return p


def prob_scaled_delta(levels, sigma):

    (_, delta_1, delta_2) = get_delta(levels=levels)

    sigma_scaled = sigma * np.sqrt(
        (delta_1 ** 2 + delta_2 ** 2) / 2
    )

    p = prob(levels=levels, sigma=sigma_scaled)

    return p
