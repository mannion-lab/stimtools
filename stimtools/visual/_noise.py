from __future__ import absolute_import, print_function, division

import numpy as np


def noise_image(img_size, slope_alpha=1.0, phase_src_img=None, rescale=True):
    """Generate a noise image with a particular spatial frequency slope.

    Parameters
    ----------
    img_size: integer
        Size of one dimension of the square output image.
    slope_alpha: float, optional
        Value of the alpha parameter in the 1/f^alpha equation.
    phase_src_img: 2D array of floats or None, optional
        Source image from which to calculate the phase distribution. If
        ``None``, a random array is generated.
    rescale: bool, optional
        Whether to scale the output to [0,1]

    """

    (x, y) = np.mgrid[-img_size / 2 : +img_size / 2, -img_size / 2 : +img_size / 2]

    dist_mat = np.sqrt(x ** 2 + y ** 2)

    dist_mat /= img_size / 2

    # yep, i know
    old_settings = np.seterr(divide="ignore")
    amp_mat = 1.0 / (dist_mat ** slope_alpha)
    np.seterr(divide=old_settings["divide"])

    amp_mat[np.isinf(amp_mat)] = 0.0

    if phase_src_img is None:
        phase_src_img = np.random.rand(img_size, img_size)

    phase_mat = np.angle(np.fft.fftshift(np.fft.fft2(phase_src_img)))

    img_freq = amp_mat * np.cos(phase_mat) + 1j * (amp_mat * np.sin(phase_mat))

    img = np.real(np.fft.ifft2(np.fft.fftshift(img_freq)))

    if rescale:
        img += np.abs(img.min())
        img /= np.max(img)

    return img
