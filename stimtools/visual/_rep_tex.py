from __future__ import absolute_import, print_function, division

import numpy as np

try:
    import psychopy.visual
except ImportError:
    pass


def rep_tex(
    img_size,
    win=None,
    n_dots=100,
    dot_size_pix=5.0,
    extra_args=None,
    random_seed=None,
    random_polarity=False,
    dot_shape="gauss",
    return_alpha=False
):
    """Generate a repeatable texture from randomly-positioned dots.

    Parameters
    ----------
    img_size : two-item list of integers
        Size of the output image, (x, y)
    win : psychopy Window
        If not provided, a window is opened and closed and the screenshot
        returned.
    n_dots : integer
        Number of dots to be randomly distributed over `img_size`.
    dot_size_pix : number
        Size of each dot, in pixels.
    extra_args : dict or None
        Any extra arguments to be passed to psychopy's `ElementArrayStim`.
    random_seed : integer or None
        Value to seed the random number generator.
    random_polarity : bool
        Whether each dot should have random contrast polarity.
    dot_shape : string
        What form each dot should take.
    return_alpha : bool
        Whether to also return an alpha mask; requires `win` to be `None`.

    """

    if win is None:
        win = psychopy.visual.Window(size=img_size, fullscr=False, units="pix")
        close_at_end = True
    else:
        close_at_end = False

    if extra_args is None:
        extra_args = {}

    rand = np.random.RandomState(random_seed)

    dot_positions = rand.rand(n_dots, 2)

    for (i_dim, dim_size) in enumerate(img_size):
        dot_positions[:, i_dim] *= dim_size
        dot_positions[:, i_dim] -= (dim_size / 2)

    if random_polarity:
        dot_contrasts = np.random.choice([-1, +1], n_dots)
    else:
        dot_contrasts = np.ones(n_dots)

    xy = []
    contrasts = []

    for x_offset in [-1, 0, +1]:
        for y_offset in [-1, 0, +1]:

            offset_positions = np.copy(dot_positions)

            offset_positions[:, 0] += x_offset * img_size[0]
            offset_positions[:, 1] += y_offset * img_size[1]

            xy.append(offset_positions)

            contrasts.append(dot_contrasts)

    xy = np.concatenate(xy)
    contrasts = np.concatenate(contrasts)

    dots = psychopy.visual.ElementArrayStim(
        win=win,
        units="pix",
        nElements=xy.shape[0],
        sizes=dot_size_pix,
        contrs=contrasts,
        xys=xy,
        elementMask=dot_shape,
        elementTex=np.ones([4, 4]),
        **extra_args
    )

    if close_at_end:

        dots.draw()

        win.flip()

        return_val = np.array(win.getMovieFrame())

        if return_alpha:
            dots.contrs = 1
            win.color = [-1] * 3

            win.flip()

            dots.draw()
            win.flip()

            alpha = np.array(win.getMovieFrame())[..., 0][..., np.newaxis]

            return_val = np.concatenate([return_val, alpha], axis=-1)

        win.close()

    else:

        return_val = xy

    return return_val
