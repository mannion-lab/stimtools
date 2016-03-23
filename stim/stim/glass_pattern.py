from __future__ import absolute_import, print_function, division

import numpy as np

import psychopy.visual
import psychopy.misc
import psychopy.filters

import stim.utils


class GlassPattern(object):

    def __init__(
        self,
        win,
        size,
        n_dipoles,
        dipole_sep,
        dot_size,
        ori_type,
        ori_deg,
        ori_sigma_deg=None,
        coh=1.0,
        col_set=(+1, -1),
        pos=(0.0, 0.0),
        dot_type="gauss",
        mask_prop=(None, 1.0),
        contrast=1.0,
        coh_mod_amp=0.0,
        coh_mod_freq=0.0,
        coh_mod_ori_deg=0.0,
        coh_mod_phase=0.0,
        coh_mod_wave="sin",
        units="pix"
    ):
        """
        Glass patterns.

        Parameters
        ----------
        win: window instance
            PsychoPy window.
        size: int
            Size of the pattern region, for both width and height.
        n_dipoles: int
            Number of dipoles over the area (not taking any mask into
            consideration).
        pole_sep: float
            Distance between the dipole elements.
        dot_size: float
            Dot size. The meaning of this parameter depends on the value of
            `dot_type`.
        ori_type: string, {"trans", "polar"}
           Orientation space of the pattern.
        ori_deg: float
            The signal orientation, in degrees.
        ori_sigma_deg: float or None
            Width of the distribution from which the dipole orientations are
            drawn. If None, then all dipoles have the same orientation.
        coh: float, 0 <= coh <= 1
            Pattern coherence (the proportion of signal dipoles).
        col_set: list of floats
            Set of intensity values for the dipoles. Default gives mixed black
            and white dipoles.
        pos: 2 item list of numbers
            Centre position.
        dot_type: string
            Form of each individual dot.
        mask_prop: two-item collection of floats
            Extent of dot visibility for inner and outer extents of an annulus.
            These are in normalised units.
        contrast: float
            Contrast of the dots.
        coh_mod_amp: float
            Amplitude of a sinusoidal spatial coherence modulation. The
            coherence will peak/trough at `coh` +- `coh_amp_mod`.
        coh_amp_freq: float
            Frequency of the coherence modulation, in cycles per unit.
        coh_amp_ori_deg: float
            Orientation of the coherence modulation, in degrees.
        coh_mod_phase: float
            Phase of the coherence modulation, in radians.
        coh_mod_wave: string, {"sin", "sqr"}
            Shape of the coherence modulation.
        units: string
            Format of the parameters, in psychopy format (e.g. "pix", "deg").

        """

        self._win = win

        self._n_dipoles = n_dipoles
        self._units = units

        self._stim = psychopy.visual.ElementArrayStim(
            win=self._win,
            autoLog=False,
            elementTex=None,
            nElements=self._n_dots,
            units=self._units
        )

        self.size = size
        self.dipole_sep = dipole_sep
        self.dot_size = dot_size
        self.ori_type = ori_type
        self.ori_deg = ori_deg
        self.ori_sigma_deg = ori_sigma_deg
        self.coh = coh
        self.col_set = col_set
        self.contrast = contrast
        self.pos = pos
        self.dot_type = dot_type
        self.mask_prop = mask_prop
        self.coh_mod_amp = coh_mod_amp
        self.coh_mod_freq = coh_mod_freq
        self.coh_mod_ori_deg = coh_mod_ori_deg
        self.coh_mod_phase = coh_mod_phase
        self.coh_mod_wave = coh_mod_wave

        self._distribute_dp_req = True
        self._distribute_dots_req = True
        self._mask_req = True
        self._contrast_req = True

        self.distribute()
        self.set_contrast()
        self.set_mask()


    @property
    def _half_size(self):
        return self._size / 2.0

    @property
    def _n_dots(self):
        return self._n_dipoles * 2

    @property
    def _n_dipole_types(self):

        n_signal = int(self._n_dipoles * self.coh)
        n_noise = self._n_dipoles - n_signal

        return (n_signal, n_noise)

    @property
    def _n_signal_dipoles(self):
        return self._n_dipole_types[0]

    @property
    def _n_noise_dipoles(self):
        return self._n_dipole_types[1]

    @property
    def _update_req(self):
        return (
            self._distribute_dp_req or
            self._distribute_dots_req or
            self._contrast_req or
            self._mask_req
        )

    @property
    def _dipole_centre_sep(self):
        return self._dipole_sep / 2.0

    @property
    def density(self):
        return self._n_dots / float(self._size ** 2)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size
        self._distribute_dp_req = True
        self._distribute_dots_req = True
        self._mask_req = True

    @property
    def ori_deg(self):
        return self._ori_deg

    @ori_deg.setter
    def ori_deg(self, ori_deg):
        self._ori_deg = ori_deg
        self._distribute_dots_req = True

    @property
    def dipole_sep(self):
        return self._dipole_sep

    @dipole_sep.setter
    def dipole_sep(self, dipole_sep):
        self._dipole_sep = dipole_sep
        self._distribute_dots_req = True

    @property
    def dot_size(self):
        return self._dot_size

    @dot_size.setter
    def dot_size(self, dot_size):
        self._dot_size = dot_size
        self._stim.sizes = self._dot_size

    @property
    def coh(self):
        return self._coh

    @coh.setter
    def coh(self, coh):
        self._coh = coh
        self._distribute_dots_req = True

    @property
    def col_set(self):
        return self._col_set

    @col_set.setter
    def col_set(self, col_set):
        self._col_set = col_set

        self._dot_cols = np.repeat(
            self._col_set,
            self._n_dots / len(self._col_set)
        )

        self._contrast_req = True

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, pos):
        self._pos = pos
        self._stim.fieldPos = pos

    @property
    def dot_type(self):
        return self._dot_type

    @dot_type.setter
    def dot_type(self, dot_type):
        self._dot_type = dot_type
        self._stim.elementMask = self._dot_type

    @property
    def mask_prop(self):
        return self._mask_prop

    @mask_prop.setter
    def mask_prop(self, mask_prop):
        self._mask_prop = mask_prop
        self._mask_req = True

    @property
    def coh_mod_wave(self):
        return self._coh_mod_wave

    @coh_mod_wave.setter
    def coh_mod_wave(self, coh_mod_wave):
        self._coh_mod_wave = coh_mod_wave
        self._distribute_dots_req = True

    @property
    def coh_mod_amp(self):
        return self._coh_mod_amp

    @coh_mod_amp.setter
    def coh_mod_amp(self, coh_mod_amp):
        self._coh_mod_amp = coh_mod_amp
        self._distribute_dots_req = True

    @property
    def coh_mod_freq(self):
        return self._coh_mod_freq

    @coh_mod_freq.setter
    def coh_mod_freq(self, coh_mod_freq):
        self._coh_mod_freq = coh_mod_freq
        self._distribute_dots_req = True

    @property
    def coh_mod_ori_deg(self):
        return self._coh_mod_ori_deg

    @coh_mod_ori_deg.setter
    def coh_mod_ori_deg(self, coh_mod_ori_deg):
        self._coh_mod_ori_deg = coh_mod_ori_deg
        self._distribute_dots_req = True

    @property
    def coh_mod_phase(self):
        return self._coh_mod_phase

    @coh_mod_phase.setter
    def coh_mod_phase(self, coh_mod_phase):
        self._coh_mod_phase = coh_mod_phase
        self._distribute_dots_req = True

    @property
    def contrast(self):
        return self._contrast

    @contrast.setter
    def contrast(self, contrast):
        self._contrast = contrast
        self._contrast_req = True

    def set_contrast(self):

        i_rand = np.random.permutation(self._n_dipoles)

        i_order = []

        for i in i_rand:
            i_order.extend([i * 2, i * 2 + 1])

        self._stim.contrs = (self._contrast * self._dot_cols)[i_order]
        self._contrast_req = False

    def set_mask(self):

        (_, r) = psychopy.misc.cart2pol(
            self._dipole_xy[:, 0],
            self._dipole_xy[:, 1]
        )

        r /= (self.size / 2.0)

        self._mask = np.zeros(self._n_dipoles)

        in_mask = np.logical_and(
            r >= self._mask_prop[0],
            r < self._mask_prop[1]
        )

        self._mask[in_mask] = 1

        self._mask = np.repeat(self._mask, 2)

        self._stim.opacities = self._mask

        self._mask_req = False

    def distribute(self):

        self.distribute_dipoles()
        self.distribute_dots()

    def distribute_dipoles(self):

        self._dipole_xy = np.random.uniform(
            low=-self._half_size,
            high=+self._half_size,
            size=(self._n_dipoles, 2)
        )

        self._distribute_dp_req = False

    def distribute_dots(self):

        if self._distribute_dp_req:
            raise ValueError(
                "Trying to generate dots, but dipoles need updating"
            )

        # orientation in the different convention
        ori_conv = np.radians(-stim.utils.math_to_nav_polar(self.ori_deg))

        thetas = np.empty((self._n_dipoles))
        thetas.fill(np.NAN)

        for i_dipole in xrange(self._n_dipoles):

            (x, y) = self._dipole_xy[i_dipole, :]

            # from -1 to 1
            signal_p = np.sin(
                self.coh_mod_freq * 2 * np.pi * (
                    y * np.sin(ori_conv) +
                    x * np.cos(ori_conv)
                ) +
                self.coh_mod_phase
            )

            if self.coh_mod_wave == "sqr":
                signal_p = np.sign(signal_p)

            # from -amp to +amp
            signal_p *= self.coh_mod_amp

            # change offset to base coh
            signal_p += self.coh

            if np.random.rand() < signal_p:

                if self.ori_sigma_deg is not None:
                    thetas[i_dipole] = np.random.normal(
                        loc=self.ori_deg,
                        scale=self.ori_sigma_deg
                    )
                else:
                    thetas[i_dipole] = self.ori_deg

            else:
                thetas[i_dipole] = np.random.uniform(0.0, 180.0)

        self._thetas = thetas

        # now we have an orientation for each dipole

        pole_dist = np.tile(
            (-self._dipole_centre_sep, +self._dipole_centre_sep),
            self._n_dipoles
        )

        if self.ori_type == "trans":

            pole_ori = np.repeat(thetas, repeats=2)

        elif self.ori_type == "polar":

            (theta, _) = psychopy.misc.cart2pol(
                self._dipole_xy[:, 0],
                self._dipole_xy[:, 1]
            )

            theta += thetas

            pole_ori = np.repeat(theta, repeats=2)

        else:
            raise ValueError("Unknown ori_type " + self.ori_type)

        (x_offset, y_offset) = psychopy.misc.pol2cart(
            pole_ori,
            pole_dist
        )

        self._dot_xy = (
            np.repeat(self._dipole_xy, repeats=2, axis=0) +
            np.vstack((x_offset, y_offset)).T
        )

        self._stim.xys = self._dot_xy

        # calculate distances while we're here
        self._dot_r = np.sqrt(np.sum(self._dot_xy ** 2, axis=1))

        self._distribute_dots_req = False


    def draw(
        self,
        ignore_update_error=False
    ):

        if self._update_req and not ignore_update_error:
            print(self._distribute_dp_req)
            print(self._distribute_dots_req)
            print(self._mask_req)
            print(self._contrast_req)
            raise ValueError(
                "Trying to draw a Glass pattern without creating a new " +
                "instance after a setting change"
            )

        self._stim.draw()


def combine_gps(gp_a, gp_b):
    """Combine two Glass pattern instances into one, shuffling the dipole draw
    order."""

    n_el = (
        gp_a._stim.nElements +
        gp_b._stim.nElements
    )

    i_rand = np.random.permutation(int(n_el / 2))

    i_order = []

    for i in i_rand:
        i_order.extend([i * 2, i * 2 + 1])

    gp = GlassPattern(
        win=gp_a._win,
        size=gp_a.size,
        n_dipoles=int(n_el / 2),
        dipole_sep=gp_a.dipole_sep,
        dot_size=gp_a.dot_size,
        ori_type=gp_a.ori_type,
        ori_deg=gp_a.ori_deg,
        ori_sigma_deg=gp_a.ori_sigma_deg,
        coh=0.0,
        col_set=(+1, -1),
        pos=gp_a.pos,
        dot_type=gp_a.dot_type,
        mask_prop=(None, 1.0),
        contrast=1.0,
        units=gp_a._units
    )

    gp._stim.xys = np.vstack(
        (
            gp_a._dot_xy,
            gp_b._dot_xy
        )
    )[i_order, :]

    gp._stim.contrs = np.hstack(
        (
            gp_a._stim.contrs,
            gp_b._stim.contrs
        )
    )[i_order]

    gp._stim.opacities = np.hstack(
        (
            gp_a._stim.opacities,
            gp_b._stim.opacities
        )
    )[i_order]

    gp._stim.sizes = np.vstack(
        (
            gp_a._stim.sizes,
            gp_b._stim.sizes
        )
    )[i_order, :]

    gp._stim.rgbs = np.vstack(
        (
            gp_a._stim.rgbs,
            gp_b._stim.rgbs
        )
    )[i_order, :]

    gp._stim.oris = np.hstack(
        (
            gp_a._stim.oris,
            gp_b._stim.oris
        )
    )[i_order]

    return gp
