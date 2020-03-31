import numpy as np
import scipy.stats

import soundfile

import brian2
import brian2hears


def get_ir_stats(ir, t_gauss_thresh=None, filt_centres=None, sr=None):

    if not isinstance(ir, np.ndarray):
        (ir, sr) = soundfile.read(ir)
    else:
        if sr is None:
            raise ValueError("Need to provide the sample rate if passing array")

    # 1) T_gauss
    (_, i_crossover, t_gauss) = calc_t_gauss(ir=ir, sr=sr, thresh=t_gauss_thresh)

    # use to split indirect component
    ir = ir[i_crossover:]

    filt_out = get_filter_output(ir=ir, sr=sr, cf=filt_centres)

    fit_out = fit_filter_output(filt_out=filt_out, sr=sr)

    (params, fit_flags, t60_by_freq, t60_broadband) = fit_out

    drr_by_freq = params[:, 1]

    ok = (t_gauss > 0) and (np.all(fit_flags == 1)) and (np.all(t60_by_freq < 15.0))

    return (
        i_crossover,
        t_gauss,
        t60_by_freq,
        t60_broadband,
        drr_by_freq,
        fit_flags,
        ok,
    )


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

    win_size = int((sr / 1_000) * win_ms)

    if thresh is None:
        thresh = get_kurtosis_threshold(win_size=win_size)

    n = len(ir)

    started = False

    kurtosis = np.full(n, np.nan)

    for i_sample in range(n):

        if (i_sample < (win_size / 2)) or ((i_sample + (win_size / 2)) > n):
            continue

        win_data = ir[(i_sample - win_size // 2) : (i_sample + win_size // 2)]

        if not started and np.all(np.abs(win_data) < 0.1):
            continue
        else:
            started = True

        kurtosis[i_sample] = scipy.stats.kurtosis(win_data)

    with np.errstate(invalid="ignore"):
        gauss_cum = np.nancumsum(kurtosis < thresh)
        nongauss_cum = np.nancumsum(kurtosis >= thresh)

    cum_diff = gauss_cum - nongauss_cum

    sign_changes = np.logical_and(
        np.sign(cum_diff[1:]) == 1,
        np.logical_or(np.sign(cum_diff[:-1]) == -1, np.sign(cum_diff[:-1]) == 0),
    )

    i_sign_changes = np.flatnonzero(sign_changes)

    crossover = i_sign_changes[-1] + 1

    t_gauss = (crossover / float(sr)) * 1_000

    if peak_rel:

        i_peak_sample = np.argmax(np.abs(ir))

        peak_ms = (i_peak_sample / float(sr)) * 1_000

        t_gauss -= peak_ms

    return (kurtosis, crossover, t_gauss)


def get_kurtosis_threshold(win_size, n_boot=10_000):
    """Use the distribution of kurtosis of a random noise sample to identify a
    threshold for unlikelyness."""

    draws = np.random.normal(loc=0.0, scale=1.0, size=(win_size, n_boot))

    ks = scipy.stats.kurtosis(a=draws, axis=0)

    thresh = scipy.stats.scoreatpercentile(ks, 97.5)

    return thresh


def get_filter_centres(low=20, high=16_000, n=33):

    return brian2hears.erbspace(low=low * brian2.Hz, high=high * brian2.Hz, N=n)


def get_filter_output(ir, sr, cf=None, dB=False, abs_conv=True):

    if cf is None:
        cf = get_filter_centres()

    bs = brian2hears.Sound(data=ir, samplerate=sr * brian2.Hz)

    bank = brian2hears.Gammatone(source=bs, cf=cf)

    output = bank.process()

    if abs_conv:
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

    fit_flags = fit_flags.astype("int")

    return (params, fit_flags, t60, t60_bb)


def fit_decay(filt_response, sr):

    t = np.arange(len(filt_response)) / float(sr)

    def err_func(params):
        return M(x=t, params=params) - filt_response

    (p, _, _, _, ier) = scipy.optimize.leastsq(
        func=err_func, x0=[-250, 50], full_output=True
    )

    # 2 The relative error between two consecutive iterates is at most ...
    # 5 Number of calls to function has reached maxfev
    # 3 Both actual and predicted relative reductions in the sum of squares
    #   are at most ...

    return (p, ier)


def M(x, params):

    (phi, drr) = params

    if -(60.0 / phi) < 0:
        return np.Inf

    y = 10 ** (((phi * x) - drr) / 20.0)

    return y
