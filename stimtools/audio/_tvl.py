
import subprocess
import tempfile
import os

import numpy as np

import soundfile
import resampy


def compute_tvl(wav, db_max, fir_type="midear", sr_orig=None):
    """Computes the 'time-varying loudness' of a waveform, using the binary
    provided at https://www.psychol.cam.ac.uk/hearing.

    Parameters
    ----------
    wav: string or numpy array.
        Path to the wav file or the waveform. Will be resampled if not 32Khz.
    db_max: number
        The level (dB SPL) produced by a full-scale sinusoid.
    fir_type: string, {"midear", "df", "ff"}
        See the program README for details on what this does.
    sr_orig: int
        Sample rate of `wav`. Only used if `wav` is an array.

    Returns
    -------
    output: (3, 2) array of floats
        The first axis is ("instantaneous", "short-term average", "long-term
        average"), and the second axis is ("sones", "phons").
    """

    try:
        tvl_path = os.environ["TVL_PATH"]
    except KeyError:
        raise ValueError(
            "The location of TVLBIN.exe was not known. Set the TVL_PATH " +
            "environment variable"
        )

    # sample rate expected by the tvl calculator
    sr_tvl = 32_000

    if not isinstance(wav, np.ndarray):
        (wav, sr_orig) = soundfile.read(wav_path)
    else:
        assert sr_orig is not None

    if sr_orig != sr_tvl:

        wav = resampy.resample(
            x=wav,
            sr_orig=sr_orig,
            sr_new=sr_tvl,
            axis=0
        )

    temp_wav_path = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    ).name

    try:
        soundfile.write(
            temp_wav_path,
            wav,
            samplerate=sr_tvl,
            subtype="PCM_16"
        )

        cmd = [
            "wine",
            "TVLBIN.exe",
            "-i", temp_wav_path,
            "-c", "(" + ",".join([f"{db_max:.0f}"] * 2) + ")",
            "-F", "(" + ",".join([f"{fir_type:s}1.32k"] * 2) + ")"
        ]

        cmd_out = subprocess.check_output(
            cmd,
            cwd=tvl_path,
            stderr=subprocess.DEVNULL
        )

    finally:
        os.remove(temp_wav_path)

    output = parse_tvl_output(output=cmd_out)

    return output


def parse_tvl_output(output):

    output = output.decode("utf8").splitlines()

    meas = []

    assert output[24] == "BOTH CHANNELS (STEREO)"

    i_start = 28

    for row_raw in output[i_start:]:

        if row_raw.replace(" ", "") == "|" * 2:
            break

        row = list(
            map(
                float,
                row_raw.replace(":", "").replace("|", "").split()
            )
        )

        row_array = np.full((3, 2), np.nan)

        (_, ins_s, ins_p, sta_s, sta_p, lta_s, lta_p) = row

        row_array[0, :] = (ins_s, ins_p)
        row_array[1, :] = (sta_s, sta_p)
        row_array[2, :] = (lta_s, lta_p)

        meas.append(row_array)

    meas = np.array(meas)

    return meas
