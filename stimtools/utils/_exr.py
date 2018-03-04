from __future__ import absolute_import, print_function, division

import numpy as np

# don't get too annoyed if package not installed
try:
    import OpenEXR
    import Imath
except ImportError:
    pass


def read_exr(exr_path, squeeze=True):
    """Read an EXR file and return a numpy array.

    Parameters
    ----------
    exr_path: string
        Path to the EXR file to read.
    squeeze: boolean, optional
        Whether to remove single channel dimensions.

    """

    exr_file = OpenEXR.InputFile(exr_path)

    channels = exr_file.header()["channels"].keys()

    data_window = exr_file.header()["dataWindow"]

    img_size = (
        data_window.max.x - data_window.min.x + 1,
        data_window.max.y - data_window.min.y + 1
    )

    pixel_type = Imath.PixelType(Imath.PixelType.FLOAT)

    if all([k in channels for k in ["Y", "A"]]):
        channel_order = ["Y", "A"]
    elif all([k in channels for k in ["R", "G", "B"]]):
        channel_order = ["R", "G", "B"]
    else:
        channel_order = channels

    img = np.full((img_size[1], img_size[0], len(channels)), np.nan)

    for (i_channel, curr_channel) in enumerate(channel_order):
        channel_str = exr_file.channel(curr_channel, pixel_type)
        channel_img = np.fromstring(channel_str, dtype=np.float32)
        channel_img.shape = (img_size[1], img_size[0])
        img[..., i_channel] = channel_img

    assert np.sum(np.isnan(img)) == 0

    exr_file.close()

    if squeeze:
        img = np.squeeze(img)

    return img


def write_exr(exr_path, img, channels):
    """Write an EXR file from a numpy array.

    Parameters
    ----------
    exr_path: string
        Path to the filename to write.
    img: 2D or 3D numpy array of floats, [0, 1]
        Image (y, x) to write.
    channels: n-item collection of strings
        Description of the channel dimension. For example: ("Y", "A"); ("R",
        "G", "B").

    """

    (h, w) = img.shape[:2]

    if img.ndim == 2:
        img = img[..., np.newaxis]

    img = np.array(img, dtype=np.float32)

    header = OpenEXR.Header(w, h)

    chan_fmt = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))

    header["channels"] = {
        channel: chan_fmt
        for channel in channels
    }

    data_dict = {
        channel: img[..., i_channel].tostring()
        for (i_channel, channel) in enumerate(channels)
    }

    exr_file = OpenEXR.OutputFile(exr_path, header)

    exr_file.writePixels(data_dict)

    exr_file.close()
