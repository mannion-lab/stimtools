
import numpy as np


def rms_over_time(waveform, bin_samples):

    half_bin = int(bin_samples / 2)

    rms = np.array(
        [
            np.std(waveform[(i_curr - half_bin):(i_curr + half_bin)])
            for i_curr in range(half_bin, len(waveform) - half_bin)
        ]
    )

    return rms
