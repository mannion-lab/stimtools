import os

import numpy as np


def ar_expressions(session):
    """Get the expressions and their associated numbers for the AR face
    database."""

    if session not in [1, 2]:
        raise ValueError("Session number must be 1 or 2")

    session_offset = (session - 1) * 13

    expressions = {
        "neutral": 1 + session_offset,
        "smile": 2 + session_offset,
        "anger": 3 + session_offset,
        "scream": 4 + session_offset,
        "left_lit": 5 + session_offset,
        "right_lit": 6 + session_offset,
        "both_lit": 7 + session_offset,
        "sunnies": 8 + session_offset,
        "sunnies_left_lit": 9 + session_offset,
        "sunnies_right_lit": 10 + session_offset,
        "scarf": 11 + session_offset,
        "scarf_left_lit": 12 + session_offset,
        "scarf_right_lit": 13 + session_offset,
    }

    return expressions


def ar_read(sex, person_id, session, expression="neutral", db_path=""):
    """Read an image from the AR face database.

    Parameters
    ----------
    sex: string, {"m", "f"}
        Person sex.
    person_id: int
        Person identifier.
    session: int, {1, 2}
        Which session the image was collected in.
    expression: string, default is 'neutral'
        Person's expression. See `ar_expressions` for keys.
    db_path: string
        Path to the disk location containing the images.

    Returns
    -------
    img: (576, 768, 3) array of uint8
        The image.

    """

    exp = ar_expressions(session=session)

    exp_num = exp[expression]

    filename = "{s:s}-{p_id:03d}-{e:n}.raw".format(s=sex, p_id=person_id, e=exp_num)

    img_path = os.path.join(db_path, filename)

    img = ar_img_read(img_path=img_path)

    return img


def ar_img_read(img_path):
    """Read an image from the AR face database, given a filename."""

    if img_path.endswith(".Z"):
        raise ValueError("Compressed images not supported. Use 'uncompress' first")

    channels = 3
    width = 576
    height = 768

    img_flat = np.fromfile(file=img_path, dtype=np.uint8)

    img = np.reshape(img_flat, (channels, width, height))

    img = np.moveaxis(a=img, source=(0, 1, 2), destination=(2, 0, 1))

    return img
