import numpy as np

try:
    import scipy.signal
    import scipy.ndimage
except ImportError:
    pass

try:
    import psychopy.visual
    import psychopy.event
except (ImportError, TypeError):
    pass

import stimtools.utils


class SFMBoundary:
    def __init__(
        self, win, bg_size_pix, fg_size_pix, bg_n_dots, dot_size_pix, fg_bg_phase_diff
    ):

        self._win = win
        self._bg_size_pix = bg_size_pix
        self._fg_size_pix = fg_size_pix
        self._bg_n_dots = bg_n_dots
        self._dot_size_pix = dot_size_pix
        self._fg_bg_phase_diff = fg_bg_phase_diff

        base_img = np.zeros(self._bg_size_pix + [2])

        for i_img in range(2):

            dot_loc = np.vstack(
                [
                    np.random.randint(low=0, high=bg_dim_size_pix, size=self._bg_n_dots)
                    for bg_dim_size_pix in self._bg_size_pix
                ]
            ).T

            for i_dot in range(self._bg_n_dots):
                base_img[dot_loc[i_dot, 0], dot_loc[i_dot, 1], i_img] = 1

            base_img[..., i_img] = scipy.ndimage.filters.gaussian_filter(
                input=base_img[..., i_img], sigma=self._dot_size_pix, mode="wrap"
            )

        self.dot_loc = dot_loc

        (bg_img, bg_img_mask) = stimtools.utils.pad_image(
            img=base_img[..., 0], calc_mask=True
        )

        bg_img = bg_img / 0.08 * -1

        self._bg_tex = psychopy.visual.GratingStim(
            win=self._win,
            tex=bg_img,
            mask=bg_img_mask,
            size=bg_img.shape,
            units="pix",
            interpolate=False,
            autoLog=False,
        )

        fg_img = stimtools.utils.pad_image(img=base_img[..., 1])

        fg_img = fg_img / 0.08 * -1

        fg_img_mask = np.ones(fg_img.shape) * -1

        fg_img_mask[: self._fg_size_pix[1], : self._fg_size_pix[0]] = 1

        fg_img_mask = np.roll(
            np.roll(
                fg_img_mask,
                shift=-int(fg_img_mask.shape[0] / 2 + self._fg_size_pix[0] / 2),
                axis=1,
            ),
            shift=-int(fg_img_mask.shape[1] / 2 + self._fg_size_pix[1] / 2),
            axis=0,
        )

        self._fg_tex = psychopy.visual.GratingStim(
            win=self._win,
            tex=fg_img,
            mask=fg_img_mask,
            size=fg_img.shape,
            units="pix",
            interpolate=False,
            autoLog=False,
        )

    def update(self, delta_t):

        self._bg_tex.phase += [delta_t, 0]
        self._fg_tex.phase -= [delta_t, 0]

    def draw(self):

        self._bg_tex.draw()
        self._fg_tex.draw()


def demo():

    win = psychopy.visual.Window(size=[400, 400], fullscr=False, units="pix")

    sfm = SFMBoundary(
        win=win,
        bg_size_pix=[256, 256],
        fg_size_pix=[64, 128],
        bg_n_dots=600,
        dot_size_pix=2,
        fg_bg_phase_diff=0,
    )

    ph_inc = 0.005

    keep_going = True

    while keep_going:

        sfm.update(ph_inc)

        sfm.draw()

        win.flip()

        win.getMovieFrame()

        keys = psychopy.event.getKeys()

        if keys:
            keep_going = False

    win.saveMovieFrames("sfm_boundary.png")

    win.close()


if __name__ == "__main__":
    demo()
