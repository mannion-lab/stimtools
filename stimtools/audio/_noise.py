from __future__ import absolute_import, print_function, division

import collections
import warnings

import numpy as np

import soundfile

import stimtools.utils


def white_noise(
    dur_s,
    rms,
    same_lr=True,
    filename=None,
    rate=44100,
    window_samples=220,
    post_pad_samples=0,
    out_of_range="error",
    rand=None,
):
    """Generates a 'white noise' waveform (Gaussian noise).

    Parameters
    ----------
    dur_s: float
        Duration, in seconds.
    rms: float or two-item sequences of floats
        Root-mean-square amplitude for the L and R channels.
    same_lr: bool, optional
        Whether the left and right channels have the same random samples.
    filename: string or None, optional
        If provided, saves the waveform as a 'wav' file.
    rate: int, optional
        Sample rate.
    window_samples: int, optional
        Number of samples to use in a Hanning window at the start and end of
        the waveform.
    post_pad_samples: int, optional
        The number of zeros to append to the waveform.
    out_of_range: string, {"warn", "error"}, or None, optional
        What to do if the waveform goes out of range.
    rand: np.random.RandomState instance or None, optional
        Random number generator.

    Returns
    -------
    y : numpy array of 16-bit integers
        A 2D array (number of samples x 2).

    """

    if rand is None:
        rand = np.random.RandomState()

    if not isinstance(rms, collections.Sequence):
        rms = [rms] * 2

    rms = np.array(rms)

    n_samples = int(dur_s * rate)

    if same_lr:
        y = rand.normal(loc=0.0, scale=1.0, size=(n_samples, 1))
        y = np.tile(y, (1, 2))
    else:
        y = rand.normal(loc=[0.0] * 2, scale=[1.0] * 2, size=(n_samples, 2))

    if window_samples > 0:
        y = stimtools.utils.apply_hanning(y, window_samples)

    y *= rms

    if out_of_range in ("warn", "error"):

        clip_req = np.logical_or(np.any(y < -1), np.any(y > +1))

        if clip_req:

            if out_of_range == "warn":
                warnings.warn("Clipping required")
            else:
                rms_str = ",".join(map(str, rms))
                raise ValueError("Clipping would be required for an RMS of " + rms_str)

    y = np.clip(y, a_min=-1, a_max=1)

    y = np.concatenate((y, np.zeros((post_pad_samples, 2))))

    if filename is not None:

        soundfile.write(
            file=filename, data=y, samplerate=rate, format="wav", subtype="PCM_16"
        )

    return y


def pink_noise(
    dur_s,
    rms,
    filename=None,
    rate=44100,
    window_samples=220,
    post_pad_samples=10000,
    out_of_range=None,
    seed=None,
):
    """Generates a 'pink noise' (1/f) waveform, within the range for 20Hz to
    20kHz.

    Parameters
    ----------
    dur_s : float
        Duration, in seconds.
    rms : float or two-item sequences of floats
        Root-mean-square amplitude for the L and R channels.
    filename : string or None, optional
        If provided, saves the waveform as a 'wav' file.
    rate : int, optional
        Sample rate.
    window_samples : int, optional
        Number of samples to use in a Hanning window at the start and end of
        the waveform.
    post_pad_samples : int, optional
        The number of zeros to append to the waveform.
    out_of_range : string, {"warn", "err"}, or None, optional
        What to do if the waveform goes out of range.
    seed : int or None, optional
        Seed for the random number generator.

    Returns
    -------
    y : numpy array of 16-bit integers
        A 2D array (number of samples x 2).

    """

    if not isinstance(rms, collections.Sequence):
        rms = [rms] * 2

    rms = np.array(rms)

    n_samples = int(dur_s * rate)

    freqs = np.fft.fftfreq(n_samples) * rate

    with np.errstate(divide="ignore"):
        amps = 1.0 / np.abs(freqs)

    amps[np.isinf(amps)] = 0.0

    i_audible = np.logical_and(freqs >= 20, freqs <= 20000)

    amps[np.logical_not(i_audible)] = 0.0

    rand = np.random.RandomState(seed=seed)

    uniform = rand.uniform(-1, 1, n_samples)

    phases = np.angle(np.fft.fft(uniform))

    freq_domain = amps * np.cos(phases) + 1j * amps * np.sin(phases)

    y = np.real(np.fft.ifft(freq_domain))

    if window_samples > 0:
        y = stimtools.utils.apply_hanning(y, window_samples)

    y = (y - np.mean(y)) / np.std(y)

    # convert to stereo
    y = np.tile(y[:, np.newaxis], (1, 2))

    y *= rms

    if out_of_range in ("warn", "error"):

        clip_req = np.logical_or(np.any(y < -1), np.any(y > +1))

        if clip_req:

            if out_of_range == "warn":
                warnings.warn("Clipping required")
            else:
                raise ValueError("Clipping would be required")

    y = np.clip(y, a_min=-1, a_max=1)

    y = np.concatenate((y, np.zeros((post_pad_samples, 2))))

    if filename is not None:

        soundfile.write(
            file=filename, data=y, samplerate=rate, format="wav", subtype="PCM_16"
        )

    return y
