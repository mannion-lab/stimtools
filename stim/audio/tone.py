
import collections

import numpy as np
import scipy.io.wavfile


def pure_tone(
    freq,
    dur_s,
    amplitude,
    filename=None,
    rate=44100,
    window_samples=220,
    post_pad_samples=10000
):

    if not isinstance(amplitude, collections.Sequence):
        amplitude = [amplitude] * 2

    amplitude = np.array(amplitude)

    n_samples = int(dur_s * rate)

    x = np.arange(0.0, 1.0, 1.0 / n_samples)

    y = np.sin(2 * np.pi * x * freq * dur_s)

    if window_samples > 0:

        hamming_win = np.hamming(2 * window_samples + 1)

        y[:window_samples] *= hamming_win[:window_samples]

        y[-window_samples:] *= hamming_win[window_samples + 1:]

    y = np.concatenate((y, np.zeros(post_pad_samples)))

    # convert to stereo
    y = np.tile(y[:, np.newaxis], (1, 2))

    y *= amplitude

    max_amp = 32767.0

    y = (y * max_amp).astype("int16")

    if filename is not None:

        scipy.io.wavfile.write(
            filename=filename,
            rate=rate,
            data=y
        )

    return y
