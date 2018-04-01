
from __future__ import absolute_import, print_function, division

import numbers
import warnings

import numpy as np

try:
    import cv2
except ImportError:
    pass


def read_frames(vid_path, frames=None, convert_colour=True):
    """Read images from video files (requires OpenCV).

    Parameters
    ----------
    vid_path: string
        Path of the video file.
    frames: integer, n-item collection of integers, or None, optional.
        Frame numbers to return. If `None`, returns all frames.
    convert_colour: boolean, optional
        Whether to convert the colour from BGR to RGB, which is sometimes
        necessary.

    Returns
    -------
    caps: numpy array of 8-bit integers, (f, h, w, c)

    """

    vid = cv2.VideoCapture(vid_path)

    if isinstance(frames, numbers.Number):
        frames = [frames]

    elif frames is None:

        total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))

        frames = range(total_frames)

    n_frames = len(frames)

    (w, h) = [
        int(vid.get(prop))
        for prop in [cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT]
    ]

    caps = np.full((n_frames, h, w, 3), np.nan, dtype=np.uint8)

    for (i_frame, frame_num) in enumerate(frames):

        vid.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

        (read_ok, frame) = vid.read()

        if not read_ok:
            warning = "Unable to read past frame {n:d} of {t:d}".format(
                n=(frame_num - 1), t=n_frames
            )
            warnings.warn(warning)
            n_frames = frame_num
            break

        if convert_colour:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        caps[i_frame, ...] = frame

    caps = caps[:n_frames, ...]

    assert np.sum(np.isnan(caps)) == 0

    return caps
