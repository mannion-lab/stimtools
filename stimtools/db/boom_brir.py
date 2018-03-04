

import os

import numpy as np

import soundfile


def get_base_path():

    return os.path.expanduser("~/science/db/boom_ir")


def get_db_info(base_path=None):

    if base_path is None:
        base_path = get_base_path()

    db_path = "Impulse Responses Outdoor 48kHz"

    locations = [
        location
        for location in os.listdir(
            os.path.join(base_path, db_path)
        )
        if "Designed" not in location and "DS_" not in location
    ]

    db_info = {}

    for location in locations:

        files = os.listdir(os.path.join(base_path, db_path, location))

        wav_files = [
            curr_file
            for curr_file in files
            if curr_file.endswith("wav")
        ]

        (img_file, ) = [
            curr_file
            for curr_file in files
            if curr_file.endswith("jpg")
        ]

        distances = [
            os.path.splitext(wav_file)[0].split(" ")[-1]
            for wav_file in wav_files
        ]

        db_info[location] = {
            "wav_files": wav_files,
            "distances": distances,
            "img_file": img_file
        }

    return db_info


def load_brir(location, distance, sr_khz=48, base_path=None, db_info=None):

    if base_path is None:
        base_path = get_base_path()

    if db_info is None:
        db_info = get_db_info(base_path=base_path)

    brir_path = os.path.join(
        base_path,
        "Impulse Responses Outdoor {sr:d}kHz".format(sr=sr_khz),
        location,
        "{loc:s} {d:d}m.wav".format(loc=location, d=distance)
    )

    (brir, brir_sr) = soundfile.read(file=brir_path)

    assert brir_sr == sr_khz * 1000

    return brir


def convolve(source, brir):

    if source.ndim == 1:
        source = np.repeat(
            source[:, np.newaxis],
            repeats=2,
            axis=-1
        )

    return np.concatenate(
        [
            np.convolve(
                source[:, i_channel],
                brir[:, i_channel]
            )[:, np.newaxis]
            for i_channel in range(2)
        ],
        axis=-1
    )
