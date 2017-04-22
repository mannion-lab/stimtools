from __future__ import absolute_import, print_function, division

import collections
import warnings

import numpy as np
import scipy.io.wavfile


def pink_noise(
    dur_s,
    rms,
    filename=None,
    rate=44100,
    window_samples=220,
    post_pad_samples=10000,
    out_of_range=None,
    seed=None
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
        Number of samples to use in a Hamming window at the start and end of
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

    i_audible = np.logical_and(
        freqs >= 20,
        freqs <= 20000
    )

    amps[np.logical_not(i_audible)] = 0.0

    rand = np.random.RandomState(seed=seed)

    uniform = rand.uniform(-1, 1, n_samples)

    phases = np.angle(np.fft.fft(uniform))

    freq_domain = amps * np.cos(phases) + 1j * amps * np.sin(phases)

    y = np.real(np.fft.ifft(freq_domain))

    if window_samples > 0:

        hamming_win = np.hamming(2 * window_samples + 1)

        y[:window_samples] *= hamming_win[:window_samples]

        y[-window_samples:] *= hamming_win[window_samples + 1:]

    y = ((y - np.mean(y)) / np.std(y))

    # convert to stereo
    y = np.tile(y[:, np.newaxis], (1, 2))

    y *= rms

    max_amp = 32767.0

    y *= max_amp

    if out_of_range in ("warn", "error"):

        clip_req = np.logical_or(
            np.any(y < -max_amp),
            np.any(y > +max_amp)
        )

        if clip_req:

            if out_of_range == "warn":
                warnings.warn("Clipping required")
            else:
                raise ValueError("Clipping would be required")

    y = np.clip(y, a_min=-max_amp, a_max=max_amp)

    y = np.concatenate((y, np.zeros((post_pad_samples, 2))))

    y = y.astype("int16")

    if filename is not None:
        scipy.io.wavfile.write(
            filename=filename,
            rate=rate,
            data=y
        )

    return y
