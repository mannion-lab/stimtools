from __future__ import absolute_import, print_function, division

import numpy as np
import numpy.testing as npt


def apply_hanning(waveform, window_samples, section="both"):
    """Applies a Hanning window to a waveform.

    Parameters
    ----------
    waveform: array
        Waveform to apply the window to.
    window_samples: int
        Number of samples in the window (one-sided). This encompassess the (0, 1) range.
    section: string, {"both", "start", "end"}
        Whether to apply the window to the start, end, or both sections of the waveform.

    Returns
    -------
    out: array
        The `waveform` data, after windowing.

    """

    if section not in ["both", "start", "end"]:
        raise ValueError("Unknown `section`")

    if waveform.ndim == 1:
        waveform = waveform[:, np.newaxis]

    hanning_win = np.hanning((2 * (window_samples - 1)) + 1)

    window = hanning_win[:window_samples][:, np.newaxis]

    npt.assert_almost_equal(window[0], 0.0)
    npt.assert_almost_equal(window[-1], 1.0)

    if section == "both" or section == "start":
        waveform[:window_samples, :] *= window
    if section == "both" or section == "end":
        waveform[-window_samples:, :] *= window[::-1]

    waveform = np.squeeze(waveform)

    return waveform
