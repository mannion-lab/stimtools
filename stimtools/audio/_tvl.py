
import subprocess
import tempfile
import os

import numpy as np

import soundfile
import resampy


def compute_tvl(wav_path, db_max, fir_type="midear"):

    try:
        tvl_path = os.environ["TVL_PATH"]
    except KeyError:
        raise ValueError(
            "The location of TVLBIN.exe was not known. Set the TVL_PATH " +
            "environment variable"
        )

    # sample rate expected by the tvl calculator
    sr_tvl = 32_000

    (waveform, sr_orig) = soundfile.read(wav_path)

    if sr_orig != sr_tvl:

        waveform = resampy.resample(
            x=waveform,
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
            waveform,
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
