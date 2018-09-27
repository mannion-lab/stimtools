import numpy as np


def fit_rms_db_measurements(rms, db):
    """Fit the relationship between waveform RMS and dB SPL.

    Parameters
    ----------
    rms: array of floats
        Waveform RMS.
    db: array of floats
        Measured dB SPL levels.

    Returns
    -------
    coefs: two-item list of floats
        Polynomial coefficients.

    """

    log_rms = np.log10(rms)

    coefs = np.polyfit(x=log_rms, y=db, deg=1)

    return coefs


def rms_to_db_from_coefs(rms, coefs):
    """Convert an RMS level to dB, given a set of calibration coefficients.

    Parameters
    ----------
    rms: float
        Waveform RMS level.
    coefs: two-item list of floats
        Polynomial coefficients, as returned by ``fit_rms_db_measurements``

    Returns
    -------
    db: float
        The dB level corresponding to this RMS, according to the calibration.

    """

    return np.polyval(coefs, np.log10(rms))


def db_to_rms_from_coefs(db, coefs):
    """Convert an dB level to RMS, given a set of calibration coefficients.

    Parameters
    ----------
    db: float
        Desired dB level.
    coefs: two-item list of floats
        Polynomial coefficients, as returned by ``fit_rms_db_measurements``

    Returns
    -------
    rms: float
        The RMS level corresponding to this dB, according to the calibration.

    """

    p = np.poly1d(coefs)

    try:
        db = list(db)
    except TypeError:
        db = [db]

    rms = np.array(
        [
            10 ** ((p - curr_db).roots[0])
            for curr_db in db
        ]
    )

    if rms.size == 1:
        rms = rms[0]

    return rms
