from __future__ import absolute_import, print_function, division

import collections
import warnings

import numpy as np

import soundfile

import stimtools.utils


def pure_tone(
    freq,
    dur_s,
    amplitude,
    phase=0.0,
    filename=None,
    rate=44100,
    window_samples=220,
    post_pad_samples=0
):
    """Generates a pure tone waveform.

    Parameters
    ----------
    freq: float
        Frequency, in Hz.
    dur_s: float
        Duration, in seconds.
    amplitude: float or two-item sequence of floats, both [0, 1]
        Sine wave amplitude for the L and R channels.
    phase: float, optional
        Phase of the sinusoid, in radians.
    filename : string or None, optional
        If provided, saves the waveform as a 'wav' file.
    rate : int, optional
        Sample rate.
    window_samples : int, optional
        Number of samples to use in a Hanning window at the start and end of
        the waveform.
    post_pad_samples : int, optional
        The number of zeros to append to the waveform.

    Returns
    -------
    y : numpy array of 16-bit integers
        A 2D array (number of samples x 2).

    """

    if not isinstance(amplitude, (collections.Sequence, np.ndarray)):
        amplitude = [amplitude] * 2

    amplitude = np.array(amplitude)

    n_samples = int(dur_s * rate)

    x = np.arange(0.0, 1.0, 1.0 / n_samples)

    y = np.sin(2 * np.pi * x * freq * dur_s + phase)

    if window_samples > 0:
        y = stimtools.utils.apply_hanning(y, window_samples)

    y = np.concatenate((y, np.zeros(post_pad_samples)))

    # convert to stereo
    y = np.tile(y[:, np.newaxis], (1, 2))

    y *= amplitude

    if np.all(y[0, :] != 0):
        warnings.warn("Waveform does not start at 0")

    if np.all(y[-1, :] != 0):
        warnings.warn("Waveform does not end at 0")

    if filename is not None:

        soundfile.write(
            file=filename,
            data=y,
            samplerate=rate,
            format="WAV",
            subtype="PCM_16"
        )

    return y
