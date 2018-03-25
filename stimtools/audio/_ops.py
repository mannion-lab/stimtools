
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
    return amp * (1.0 / np.sqrt(2))


def rms_to_amp(rms):
    return rms * np.sqrt(2)
