from builtins import range

import numpy as np
import scipy.stats

import soundfile

try:
    import brian
    import brian.hears
except ImportError:
    pass


def load_ir(wav_path, channel=0, split=False):
    """Load an IR from a wav file.

    Parameters
    ----------
    wav_path: string
        Location of the wav file.
    channel: int, optional
        Which channel to load.
    split: bool, optional
        Whether to split into 'direct' and 'diffuse' components.

    Returns
    -------
    wav: array of floats or list thereof.
        Waveform.
    sr: int
        Sample rate.

    """

    (wav, sr) = soundfile.read(wav_path, always_2d=True)

    wav = wav[:, channel]

    if split:
        (_, i_x, _) = calc_t_gauss(ir=wav, sr=sr)

        wav = (wav[:i_x], wav[i_x:])

    return (wav, sr)


def calc_t_gauss(ir, sr, win_ms=10, thresh=None, peak_rel=True):
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
    peak_rel: bool, optional
        Whether `t_gauss` is relative to the time of the peak signal.

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

        if (
            (n_gauss > 0) and
            (n_nongauss > 0) and
            (n_gauss > n_nongauss) and
            (i_sample > np.argmax(ir))
        ):

            crossover = i_sample
            break

    t_gauss = (crossover / float(sr)) * 1000.0

    if peak_rel:

        i_peak_sample = np.argmax(ir)

        peak_ms = (i_peak_sample / float(sr)) * 1000.0

        t_gauss -= peak_ms

    return (kurtosis, crossover, t_gauss)


def get_kurtosis_threshold(win_size, n_boot=10000):
    """Use the distribution of kurtosis of a random noise sample to identify a
    threshold for unlikelyness."""

    draws = np.random.normal(loc=0.0, scale=1.0, size=(win_size, n_boot))

    ks = scipy.stats.kurtosis(a=draws, axis=0)

    thresh = scipy.stats.scoreatpercentile(ks, 97.5)

    return thresh


def get_filter_centres(low=20, high=16000, n=33):

    return brian.hears.erbspace(
        low * brian.Hz,
        high * brian.Hz,
        n
    )


def get_filter_output(ir, sr, cf=None, dB=False):

    if cf is None:
        cf = get_filter_centres()

    bs = brian.hears.Sound(data=ir, samplerate=sr * brian.Hz)

    bank = brian.hears.Gammatone(source=bs, cf=cf)

    output = bank.process()

    output = np.abs(output)

    if dB:
        output = 20 * np.log10(output)

    return output


def fit_filter_output(filt_out, sr):

    n_k = filt_out.shape[1]

    params = np.full((n_k, 2), np.nan)

    fit_flags = np.full(n_k, np.nan)

    for i_k in range(n_k):
        fit_out = fit_decay(filt_out[:, i_k], sr)
        (params[i_k, :], fit_flags[i_k]) = fit_out

    t60 = -(60.0 / params[:, 0])

    t60_bb = np.median(t60)

    return (params, fit_flags, t60, t60_bb)


def fit_decay(filt_response, sr):

    t = np.arange(len(filt_response)) / float(sr)

    def err_func(params):
        return M(x=t, params=params) - filt_response

    (p, _, _, _, ier) = scipy.optimize.leastsq(
        func=err_func,
        x0=[-250, 50],
        full_output=True
    )

    return (p, ier)


def M(x, params):

    (phi, drr) = params

    if -(60.0 / phi) < 0:
        return np.Inf

    y = 10 ** (((phi * x) - drr) / 20.0)

    return y