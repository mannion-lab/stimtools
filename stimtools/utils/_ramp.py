import numpy as np


def raised_cosine(n_peak, n_flank):
    """Generates a 'raised cosine' profile. These are often useful for ramping stimulus
    opacity in and out.

    Parameters
    ----------
    n_peak: int
        Number of samples at peak level (1.0).
    n_flank: int
        Number of samples per flank. This is inclusive of the zero sample but
        exclusive of the peak sample.

    Returns
    -------
    profile: numpy array of floats between 0.0 and 1.0
        The raised cosine profile. The length is `n_peak` + `n_flank * 2`.
    """

    flank_thetas = np.linspace(0.0, np.pi, n_flank, endpoint=False)

    flank = -np.cos(flank_thetas)

    peak = np.ones(n_peak)

    profile = np.concatenate((flank, peak, flank[::-1]))

    return profile
