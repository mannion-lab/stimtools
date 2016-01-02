
# UNFINISHED
#  - use properties
#  - general cleanup
#  - get rid of mask stuff

from __future__ import absolute_import, print_function, division

import numpy as np


class GlassPattern(object):
    """Glass patterns.

    Parameters
    ----------
    win : window instance
        PsychoPy window.
    size : int
        Size of the pattern region, for both width and height.
    n_dipoles : int
        Number of dipoles over the area (not taking any mask into
        consideration)
        This is half the number of dots.
    pole_sep : float
        Distance between the dipole elements, in pixels.
    dot_size : float
        Dot size, given by the sigma of a Gaussian, in pixels.
    ori_type : string, { "trans", "polar" }
        Orientation space of the pattern.
    ori_deg : float
        The pattern orientation, in degrees.
    ori_sigma_deg: float
        Width of the distribution from which the dipole orientations are drawn.
        If zero, then all dipoles have the same orientation.
    coh : float, 0 <= coh <= 1
        Pattern coherence (the proportion of signal dipoles).
    col_set : list of floats
        Set of intensity values for the dipoles. Default gives mixed black and
        white dipoles.
    pos : 2 item list of numbers
        Centre position, in `units`

    """

    def __init__(
        self,
        win,
        size,
        n_dipoles,
        pole_sep,
        dot_size,
        ori_type,
        ori_deg,
        ori_sigma_deg=0,
        coh=1.0,
        col_set=(+1, -1),
        pos=(0.0, 0.0)
    ):

        self._win = win

        self._size = size
        self._half_size = self._size / 2.0

        self._n_dipoles = n_dipoles
        self._n_dots = n_dipoles * 2
        self._dot_size = dot_size

        self._pole_sep = pole_sep
        self._pole_centre_sep = pole_sep / 2.0

        self._ori_type = ori_type
        self._ori_deg = ori_deg
        self._ori_sigma_deg = ori_sigma_deg

        self._col_set = np.array(col_set)

        self._coh = coh

        self._pos = pos

        self._dot_stim = None

        self.instantiate()

        self._set_colours()

        self._set_draw_order()

        self._dot_stim = psychopy.visual.ElementArrayStim(
            win=self._win,
            xys=(
                self._pole_locs[self._draw_order, :] +
                np.array(self._pos)
            ),
            nElements=self._n_dots,
            elementTex=None,
            elementMask="gauss",
            units="pix",
            sizes=self._dot_size,
            colors=self._cols[self._draw_order],
            interpolate=False,
            opacities=self._opac[self._draw_order]
        )

    def draw(self):
        """Draw the Glass pattern, masked if active"""

        self._dot_stim.draw()

        if self._mask_type is not None:
            self._mask.draw()

    def set_pole_sep(self, pole_sep):
        "Sets the pole separation"

        self._pole_sep = pole_sep
        self._pole_centre_sep = pole_sep / 2.0

    def set_contrast(self, contrast):
        "Sets the contrast of all the elements."

        self._dot_stim.setContrs(contrast)

    def set_coh(self, coh):
        "Sets the coherence level. N.B. This does not generate a new instance."

        self._coh = coh

    def set_ori(self, ori):
        "Sets the orientation. N.B. This does not generate a new instance."

        self._ori_deg = ori

    def set_ori_sigma(self, ori_sigma):
        "Sets the orientation sigma."

        self._ori_sigma_deg = ori_sigma

    def instantiate(
        self,
        new_loc=True,
        pole_only=False,
        randomise_order=True
    ):
        "Generates a new Glass pattern instance."

        if new_loc:
            self._set_dipole_locs()

        self._set_pole_locs()

        self._set_visibility()

        self._set_draw_order(randomise_order)

        if pole_only:
            td = [1, 0]
        else:
            td = [1, 1]

        self._opac = np.tile(td, (1, self._draw_order.shape[0] / 2)).T

        if self._dot_stim is not None:

            self._dot_stim.setXYs(self._pole_locs[self._draw_order, :])
            self._dot_stim.setOpacities(self._opac[self._draw_order])
            self._dot_stim.setColors(self._cols[self._draw_order])

            self._dot_stim.fieldPos = self._pos

    def _set_visibility(self):
        "Culls any elements outside the pattern diameter."

        # start with opacities of 1 (fully visible)
        self._opac = np.ones(self._n_dots)

        # identify the dots to be culled as those where either their x or y
        # coordinate (abs) lies outside the pattern radius
        i_clip = np.any(
            np.abs(self._pole_locs) > self._radius,
            axis=1
        )

        # set them to invisible
        self._opac[i_clip] = 0

    def _set_mask(self):
        "Sets the desired pattern mask"

        mon = self._win.monitor

        if self._units == "deg":
            pattern_diam_pix = psychopy.misc.deg2pix(self._diam, mon)
        elif self._units == "pix":
            pattern_diam_pix = self._diam

        mask_diam_pix = stimuli.utils.nearest_power_of_two(pattern_diam_pix)

        if self._units == "deg":
            mask_in_pix = psychopy.misc.deg2pix(self._mask_in * 2, mon)
            mask_out_pix = psychopy.misc.deg2pix(self._mask_out * 2, mon)
            mask_fringe_pix = psychopy.misc.deg2pix(self._mask_fringe * 2, mon)
            pos = psychopy.misc.deg2pix(self._pos, mon)

        elif self._units == "pix":
            mask_in_pix = self._mask_in * 2
            mask_out_pix = self._mask_out * 2
            mask_fringe_pix = self._mask_fringe * 2
            pos = self._pos

        in_fringe = mask_fringe_pix / mask_in_pix
        out_fringe = mask_fringe_pix / mask_out_pix

        # these need to be explicitly cast for makeMask to work
        in_prop = float(mask_in_pix / mask_diam_pix)
        out_prop = float(mask_out_pix / mask_diam_pix)

        mask_in = psychopy.filters.makeMask(
            mask_diam_pix,
            radius=in_prop,
            shape="raisedCosine",
            range=(0, 1),
            fringeWidth=in_fringe
        )

        mask_out = psychopy.filters.makeMask(
            mask_diam_pix,
            radius=out_prop,
            shape="raisedCosine",
            range=(0, 1),
            fringeWidth=out_fringe
        )

        mask = -1 * ((mask_out - mask_in) * 2 - 1)

        self._mask_array = mask

        mask_tex = np.zeros((mask_diam_pix, mask_diam_pix))

        self._mask = psychopy.visual.GratingStim(
            win=self._win,
            tex=mask_tex,
            mask=mask,
            units="pix",
            interpolate=False,
            size=mask_diam_pix,
            pos=pos
        )

    def _set_draw_order(self, randomise=True):
        "Calculates a random drawing order for the dipoles"

        self._draw_order = np.arange(self._n_dipoles)

        if randomise:
            np.random.shuffle(self._draw_order)

        # this gets a bit messy because we want to draw the elements of each
        # dipole at the same 'depth'

        self._draw_order *= 2

        self._draw_order = np.vstack((self._draw_order, self._draw_order + 1))

        self._draw_order = np.ravel(self._draw_order.T)

        self._draw_order = self._draw_order.astype("int")

    def _set_colours(self):
        "Sets the colour of each dipole element."

        i_cols = np.random.randint(
            low=0,
            high=len(self._col_set),
            size=self._n_dipoles
        )

        self._cols = np.repeat(self._col_set[i_cols], repeats=2)

        self._cols = np.tile(self._cols, (3, 1)).T

    def _set_dipole_locs(self):
        "Sets the location of each dipole centre."

        # generate the xy locations for the dipole centres, uniform random over
        # area
        self._dipole_locs = np.random.uniform(
            low=-self._radius,
            high=+self._radius,
            size=(self._n_dipoles, 2)
        )

    def _set_pole_locs(self):
        "Sets the location of each dipole element"

        n_signal_dipoles = np.round(self._n_dipoles * self._coh)
        n_noise_dipoles = self._n_dipoles - n_signal_dipoles

        if self._ori_sigma_deg == 0.0:
            signal_oris = np.repeat(self._ori_deg, repeats=n_signal_dipoles)
        else:
            signal_oris = np.random.normal(
                loc=self._ori_deg,
                scale=self._ori_sigma_deg,
                size=n_signal_dipoles
            )

        noise_oris = np.random.uniform(
            low=0.0,
            high=180.0,
            size=n_noise_dipoles
        )

        dipole_oris = np.concatenate((signal_oris, noise_oris))

        pole_dist = np.tile(
            (-self._pole_centre_sep, +self._pole_centre_sep),
            self._n_dipoles
        )

        if self._ori_type == "trans":

            pole_ori = np.repeat(dipole_oris, repeats=2)

        elif self._ori_type == "polar":

            theta, _ = psychopy.misc.cart2pol(
                self._dipole_locs[:, 0],
                self._dipole_locs[:, 1]
            )

            theta += dipole_oris

            pole_ori = np.repeat(theta, repeats=2)

        else:

            raise ValueError("Unknown ori_type " + self._ori_type)

        x_offset, y_offset = psychopy.misc.pol2cart(
            pole_ori,
            pole_dist
        )

        self._pole_locs = (
            np.repeat(self._dipole_locs, repeats=2, axis=0) +
            np.vstack((x_offset, y_offset)).T
        )

