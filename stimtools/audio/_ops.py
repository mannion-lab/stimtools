import numpy as np

import scipy.signal


def convolve(source, ir):

    if source.ndim == 1 and ir.ndim == 2:
        source = np.repeat(source[:, np.newaxis], repeats=2, axis=-1)

    if ir.ndim == 1 and source.ndim == 2:
        ir = np.repeat(ir[:, np.newaxis], repeats=2, axis=-1)

    y = scipy.signal.fftconvolve(in1=source, in2=ir, mode="full", axes=0)

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


def rms_to_db(rms, ref_rms):
    return 20.0 * np.log10(rms / ref_rms)


def phon_to_sone(phon):
    return (10 ** ((phon - 40.0) / 10.0)) ** 0.30103


def sone_to_phon(sone):
    return 40 + 10 * np.log2(sone)
