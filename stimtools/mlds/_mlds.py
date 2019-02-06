

import itertools

import numpy as np


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
