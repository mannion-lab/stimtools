
import numpy as np


def new_scramble_image(img, scramble="phase", i_end=0, seed=None):
    """Perform scrambling on an image in freqency space.

    Parameters
    ----------
    img: 2D or 3D numpy array of floats
        Image to scramble
    scramble: string, ["phase", "amplitude"], optional
        What dimension to scramble
    only_scramble_single_channel: bool
        If ``img`` is 3D, this determines whether to scramble the third
        dimension with one set of random values or multiple. With
        single-channel scrambling, which Yoonessi & Kingdom (2008) call
        'phase-aligned phase-scrambling', the colour histogram is better
        preserved.

    """

    noise_shape = np.array(img.shape)[axes, ]

    tile_k = np.array(img.shape)
    tile_k[axes, ] = 1

    rand = np.random.RandomState(seed=seed)

    # convert the image to frequency space
    img_freq = np.fft.fftn(a=img)

    # get a frequency space representation of random noise
    noise_freq = np.fft.fftn(a=rand.rand(*noise_shape))



    out_amp = np.abs(img_freq)
    out_phase = np.angle(img_freq)

    if scramble == "phase":
        out_phase = np.tile(np.angle(noise_freq), tile_k)

    elif scramble == "amplitude":
        out_amp[noise_slice] = np.abs(noise_freq)

    print out_amp.shape, out_phase.shape

    # combine the image's amplitude spectrum with the random phase
    img_scrambled_freq = (
        out_amp * np.cos(out_phase) +
        1j * (out_amp * np.sin(out_phase))
    )

    # convert back into image space
    img_scrambled = np.real(
        np.fft.ifftn(a=img_scrambled_freq)
    )

    return img_scrambled


def scramble_image(img, scramble="phase", only_scramble_single_channel=False):
    """Perform scrambling on an image in freqency space.

    Parameters
    ----------
    img: 2D or 3D numpy array of floats
        Image to scramble
    scramble: string, ["phase", "amplitude"], optional
        What dimension to scramble
    only_scramble_single_channel: bool
        If ``img`` is 3D, this determines whether to scramble the third
        dimension with one set of random values or multiple. With
        single-channel scrambling, which Yoonessi & Kingdom (2008) call
        'phase-aligned phase-scrambling', the colour histogram is better
        preserved.

    """

    # convert the image to frequency space
    img_freq = np.fft.fft2(a=img, axes=[0, 1])

    if only_scramble_single_channel:
        noise_shape = img_freq.shape[:2]
    else:
        noise_shape = img_freq.shape

    # get a frequency space representation of random noise
    noise_freq = np.fft.fft2(
        a=np.random.rand(*noise_shape),
        axes=[0, 1]
    )

    if scramble == "phase":
        out_amp = np.abs(img_freq)
        out_phase = np.angle(noise_freq)

        if only_scramble_single_channel and img.ndim == 3:
            out_phase = np.dstack([out_phase] * 3)

    elif scramble == "amplitude":
        out_amp = np.abs(noise_freq)
        out_phase = np.angle(img_freq)

        if only_scramble_single_channel and img.ndim == 3:
            out_amp = np.dstack([out_amp] * 3)

    # combine the image's amplitude spectrum with the random phase
    img_scrambled_freq = (
        out_amp * np.cos(out_phase) +
        1j * (out_amp * np.sin(out_phase))
    )

    # convert back into image space
    img_scrambled = np.real(
        np.fft.ifft2(a=img_scrambled_freq, axes=[0, 1])
    )

    return img_scrambled
