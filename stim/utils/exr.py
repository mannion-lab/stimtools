
import numpy as np

# don't get too annoyed if package not installed
try:
    import OpenEXR
except ImportError:
    pass


def write_exr(exr_path, img):
    """Write an EXR file from a numpy array.

    Parameters
    ----------
    exr_path: string
        Path to the filename to write.
    img: 2D or 3D numpy array of floats, [0, 1]
        Image (y, x) to write.

    """

    (h, w) = img.shape[:2]

    if img.ndim == 2:
        img = np.tile(
            img[..., np.newaxis],
            (1, 1, 3)
        )

    img = np.array(img, dtype=np.float32)

    header = OpenEXR.Header(w, h)

    data_dict = {
        channel: img[..., i_channel].tostring()
        for (channel, i_channel) in zip(
            ("R", "G", "B"), range(3)
        )
    }

    exr_file = OpenEXR.OutputFile(exr_path, header)

    exr_file.writePixels(data_dict)

    exr_file.close()
