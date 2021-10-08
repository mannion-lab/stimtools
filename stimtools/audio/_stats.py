import numpy as np


def rms_over_time(waveform, bin_ms, sample_rate, in_dbfs=False):

    bin_samples = int(sample_rate * (bin_ms / 1_000))

    half_bin = int(bin_samples / 2)

    i_slice = np.arange(bin_samples) - half_bin

    (n_samples, _) = waveform.shape

    i_bins = i_slice[np.newaxis, :] + np.arange(n_samples)[:, np.newaxis]

    out_of_bounds = np.logical_or(
        np.any(i_bins < 0, axis=1),
        np.any(i_bins >= n_samples, axis=1),
    )

    i_bins[out_of_bounds, :] = 0

    rms = np.sqrt(np.mean(waveform[i_bins, :] ** 2, axis=(1, 2)))

    if in_dbfs:

        # "RMS value of a full-scale sine wave is designated 0 dB FS"
        ref = 1 / np.sqrt(2)

        with np.errstate(divide="ignore"):
            rms = 20 * np.log10(rms / ref)

    rms[out_of_bounds] = np.nan

    x = np.arange(n_samples) / sample_rate * 1_000
    x[out_of_bounds] = np.nan

    return (x, rms)
