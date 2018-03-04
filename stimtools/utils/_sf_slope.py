
import numpy as np


def sf_slope(img, return_values=False):
    """Calculate the spatial frequency amplitude slope"""

    (n_rows, n_cols) = img.shape

    amp = np.abs(np.fft.fft2(img))

    fy = np.fft.fftfreq(n_rows, 1.0 / n_rows)
    fx = np.fft.fftfreq(n_cols, 1.0 / n_cols)

    f = np.sqrt(fy[:, np.newaxis] ** 2 + fx[np.newaxis, :] ** 2)

    i_valid = (f > 0)

    log_freqs = np.log(f[i_valid]).flatten()
    log_amps = np.log(amp[i_valid]).flatten()

    (slope, _) = np.polyfit(x=log_freqs, y=log_amps, deg=1)

    if return_values:
        return (slope, log_freqs, log_amps)
    else:
        return slope
