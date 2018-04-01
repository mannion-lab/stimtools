
import numpy as np


def rms_over_time(waveform, bin_samples):

    half_bin = int(bin_samples) / 2

    rms = np.array(
        [
            np.std(waveform[(i - half_bin):(i + half_bin)])
            for i in range(half_bin, len(waveform) - half_bin)
        ]
    )

    return rms
