
import numpy as np


def convolve(source, ir):

    if source.ndim == 1:
        source = np.repeat(
            source[:, np.newaxis],
            repeats=2,
            axis=-1
        )

    if ir.ndim == 1:
        ir = np.repeat(
            ir[:, np.newaxis],
            repeats=2,
            axis=-1
        )

    y = np.concatenate(
        [
            np.convolve(
                source[:, i_channel],
                ir[:, i_channel]
            )[:, np.newaxis]
            for i_channel in range(2)
        ],
        axis=-1
    )

    y = np.squeeze(y)

    return y


def amp_to_rms(amp):

    amp = np.array(amp) * (1.0 / np.sqrt(2))

    if amp.size == 1:
        amp = amp[0]

    return amp


def rms_to_amp(rms):

    rms = np.array(rms) * np.sqrt(2)

    if rms.size == 1:
        rms = rms[0]

    return rms
