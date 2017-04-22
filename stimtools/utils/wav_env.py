from __future__ import absolute_import, print_function, division

import numpy as np
import numpy.testing as npt


def apply_hanning(waveform, window_samples):
    """Applies a Hanning window to a waveform.

    Parameters
    ----------
    waveform: array
        Waveform to apply the window to.
    window_samples: int
        Number of samples in the window (one-sided). This encompassess the (0,
        1) range.

    Returns
    -------
    out: array
        The `waveform` data, after windowing.

    """

    hanning_win = np.hanning((2 * (window_samples - 1)) + 1)

    window = hanning_win[:window_samples]

    npt.assert_almost_equal(window[0], 0.0)
    npt.assert_almost_equal(window[-1], 1.0)

    waveform[:window_samples] *= window
    waveform[-window_samples:] *= window[::-1]

    return waveform
