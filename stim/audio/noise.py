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
    range_method="clip"
):

    if not isinstance(rms, collections.Sequence):
        rms = [rms] * 2

    rms = np.array(rms)

    n_samples = int(dur_s * rate)

    freqs = np.fft.fftfreq(n_samples) * rate

    with np.errstate(divide="ignore"):
        amps = 1.0 / np.abs(freqs)

    amps[np.isinf(amps)] = 0.0

    i_audible = np.logical_and(
        freqs > 20,
        freqs < 20000
    )

    amps[np.logical_not(i_audible)] = 0.0

    uniform = np.random.uniform(-1, 1, n_samples)

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

    if range_method in ("warn", "error"):

        clip_req = np.logical_or(
            np.any(y < -max_amp),
            np.any(y > +max_amp)
        )

        if clip_req:

            if range_method == "warn":
                warnings.warn("Clipping required")
            else:
                raise ValueError("Clipping would be required")

    y = np.clip(y, a_min=-max_amp, a_max=max_amp)

    y = np.concatenate((y, np.zeros((post_pad_samples, 2))))

    if filename is not None:
        scipy.io.wavfile.write(
            filename=filename,
            rate=rate,
            data=y.astype("int16")
        )

    return y
