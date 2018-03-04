
import numpy as np
import scipy.ndimage

try:
    import psychopy.visual
except ImportError:
    pass
except:  # noqa
    pass

import stimtools.utils


class FusionLock(object):

    def __init__(
        self,
        win,
        size_pix,
        outer_extent_norm,
        inner_extent_norm,
        upsample_factor=4,
        contrast=1.0,
        binary=False
    ):
        """Vergence stabiliser.

        Parameters
        ----------
        win: PsychoPy window
            Window to create the texture in.
        size_pix: int
            Size of the texture. Must be a power of two.
        outer_extent_norm, inner_extent_norm: floats
            Normalised outer and inner annulus extents. These values are
            relative to `size_pix`.
        upsample_factor: number, optional
            How much to upsample each check in the noise pattern.
        contrast: float, [0, 1]
            Noise contrast
        binary: bool
            If True, the noise is binary. If False, the noise is drawn from a
            uniform distribution.

        """

        self._win = win
        self._size_pix = size_pix
        self._outer_extent_norm = outer_extent_norm
        self._inner_extent_norm = inner_extent_norm
        self._upsample_factor = upsample_factor
        self._contrast = contrast
        self._binary = binary

        self._lowres_lock_size = int(self._size_pix / self._upsample_factor)

        lock_mask = stimtools.utils.polar_mask(
            size_pix=size_pix,
            outer_extent_norm=outer_extent_norm,
            inner_extent_norm=inner_extent_norm,
            sector_centre_deg=0.0,
            sector_central_angle_deg=361.0
        )

        self._stim = psychopy.visual.GratingStim(
            win=self._win,
            size=self._size_pix,
            units="pix",
            mask=lock_mask,
            tex=None,
            contrast=self._contrast,
            autoLog=False
        )

        self.new_instance()

    def new_instance(self):

        if self._binary:
            lowres_lock_img = np.random.choice(
                [-1, +1],
                size=[self._lowres_lock_size] * 2
            )

        else:
            lowres_lock_img = np.random.uniform(
                low=-1.0,
                high=+1.0,
                size=[self._lowres_lock_size] * 2
            )

        lock_img = scipy.ndimage.zoom(
            input=lowres_lock_img,
            zoom=self._upsample_factor,
            mode="nearest",
            prefilter=False,
            order=0
        )

        self._stim.tex = lock_img

    def draw(self):

        self._stim.draw()
