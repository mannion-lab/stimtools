
import numpy as np


def scramble_image(img, scramble="phase", axes=(0, 1), seed=None):
    """Perform scrambling on an image in freqency space.

    Parameters
    ----------
    img: 2D or 3D numpy array of floats
        Image to scramble
    scramble: string, ["phase", "amplitude"], optional
        What dimension to scramble
    axes: tuple of ints, optional
        The axes to independently scramble. The remaining axes receive the same
        scrambling. Default is to have a single scramble for colour channels.
    seed: int or None
        Seed that is used in the random generation.

    """

    noise_shape = np.ones(img.ndim, dtype=np.int)

    noise_shape[axes, ] = np.array(img.shape)[axes, ]

    tile_k = np.array(img.shape)
    tile_k[axes, ] = 1

    rand = np.random.RandomState(seed=seed)

    # get a frequency space representation of random noise
    noise_freq = np.fft.fftn(a=rand.rand(*noise_shape))

    # convert the image to frequency space
    img_freq = np.fft.fftn(a=img)

    if scramble == "phase":
        out_phase = np.tile(np.angle(noise_freq), tile_k)
        out_amp = np.abs(img_freq)

    elif scramble == "amplitude":
        out_phase = np.angle(img_freq)
        out_amp = np.tile(np.abs(noise_freq), tile_k)

    del img_freq
    del noise_freq

    # combine the image's amplitude spectrum with the random phase
    img_scrambled_freq = (
        out_amp * np.cos(out_phase) +
        1j * (out_amp * np.sin(out_phase))
    )

    del out_amp
    del out_phase

    # convert back into image space
    img_scrambled = np.real(
        np.fft.ifftn(a=img_scrambled_freq)
    )

    return img_scrambled
