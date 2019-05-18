import numpy as np


def rms_over_time(waveform, bin_samples):

    half_bin = int(bin_samples / 2)

    i_slice = np.arange(bin_samples) - half_bin

    (n_samples, _) = waveform.shape

    i_bins = i_slice[np.newaxis, :] + np.arange(n_samples)[:, np.newaxis]

    i_bins = i_bins[half_bin : -(half_bin - 1), :]

    rms = np.sqrt(np.mean(waveform[i_bins, :] ** 2, axis=(1, 2)))

    return rms
