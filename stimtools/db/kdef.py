import os
import collections

import numpy as np

import imageio

import skimage.color

import stimtools.utils

try:
    base_path = os.environ["KDEF_PATH"]
except KeyError:
    base_path = os.path.expanduser("~/science/db/kdef")


sessions = {1: "A", 2: "B"}
genders = {"male": "M", "female": "F"}
expressions = {
    "afraid": "AF",
    "angry": "AN",
    "disgusted": "DI",
    "happy": "HA",
    "neutral": "NE",
    "sad": "SA",
    "surprised": "SU"
}
poses = {
    "full-left": "FL",
    "half-left": "HL",
    "straight": "S",
    "half-right": "HR",
    "half-left": "HL"
}


def load_image(
    identity,
    gender,
    session=1,
    expression="neutral",
    pose="straight",
    pow2_pad=False,
):

    filename = "{session:s}{gender:s}{fid:02d}{exp:s}{pose:s}.JPG".format(
        session=sessions[session],
        gender=genders[gender],
        fid=identity,
        exp=expressions[expression],
        pose=poses[pose]
    )

    directory = filename[:4]

    img_path = os.path.join(
        base_path,
        "KDEF",
        directory,
        filename
    )

    img = imageio.imread(img_path)

    if pow2_pad:
        img = stim.utils.pad_image(img)

    return img
