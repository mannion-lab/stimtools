from builtins import range

import numpy as np
import scipy.stats

import soundfile


def load_ir(wav_path, channel=0, from_onset=False, n_pre=440, n_win=100):
    """Load an IR from a wav file.

    Parameters
    ----------
    wav_path: string
        Location of the wav file.
    channel: int, optional
        Which channel to load.
    from_onset: bool, optional
        Whether to chop initial silence.
    n_pre: int
        The number of samples to return before argmax, if `from_onset` is
        `True`.
    n_win: int
        The number of samples in a Hanning window to apply at the start, if
        `from_onset` is True.

    Returns
    -------
    wav: array of floats
        Waveform
    sr: int
        Sample rate.

    """

    (wav, sr) = soundfile.read(wav_path, always_2d=True)

    wav = wav[:, channel]

    if from_onset:

        i_peak = np.argmax(wav)

        i_start = i_peak - n_pre

        if i_start < 0:
            raise ValueError("Peak is closer than window")

        wav = wav[i_start:]

        win = np.hanning(n_win * 2)[:n_win]

        wav[:n_win] *= win

    return wav




def calc_t_gauss(ir, sr, win_ms=10, thresh=None):
    """Calcuate the 'time to Gaussianity'

    Parameters
    ----------
    ir: 1D array
        Impulse response.
    sr: int
        Sample rate, in Hz
    win_ms: int, optional
        Size of the window, in ms.
    thresh: number or None, optional
        The kurtosis value below which are Gaussian.

    Returns
    -------
    kurtosis: 1D array
        Kurtosis value within a window centred on the sample.
    crossover: int
        The sample at which there are more Gaussian than non-Gaussian values.
    t_gauss: float
        The time, in ms, of `crossover`.

    """

    win_size = (sr / 1000) * win_ms

    if thresh is None:
        thresh = get_kurtosis_threshold(win_size=win_size)

    n = len(ir)

    kurtosis = np.full(n, np.nan)

    diffuse = np.zeros(n, dtype=np.bool)

    for i_sample in range(n):

        if (
            (i_sample < (win_size / 2)) or
            ((i_sample + (win_size / 2)) > n)
        ):
            continue

        win_data = ir[(i_sample - win_size / 2):(i_sample + win_size / 2)]

        kurtosis[i_sample] = scipy.stats.kurtosis(win_data)

    n_gauss = 0
    n_nongauss = 0

    for i_sample in range(n):

        if np.isfinite(kurtosis[i_sample]):

            if kurtosis[i_sample] > thresh:
                n_nongauss += 1

            else:
                n_gauss += 1

        if n_gauss > 0 and n_nongauss > 0 and n_gauss > n_nongauss:
            crossover = i_sample
            break

    t_gauss = (crossover / float(sr)) * 1000.0

    return (kurtosis, crossover, t_gauss)


def get_kurtosis_threshold(win_size, n_boot=10000):
    """Use the distribution of kurtosis of a random noise sample to identify a
    threshold for unlikelyness."""

    draws = np.random.normal(loc=0.0, scale=1.0, size=(win_size, n_boot))

    ks = scipy.stats.kurtosis(a=draws, axis=0)

    thresh = scipy.stats.scoreatpercentile(ks, 97.5)

    return thresh

