
from __future__ import absolute_import, print_function, division

import numpy as np

try:
    import psychopy.visual
    import psychopy.misc
    try:
        import psychopy.visual.filters as f
        psychopy.filters = f
        del f
    except ImportError:
        import psychopy.filters

    import pyglet.gl

except ImportError:
    pass


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
        mask_ramp_prop=(0.1, 0.1),
        contrast=1.0,
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
        mask_ramp_prop: two-item collection of floats
            Extent of the contrast ramp at the edges.
        contrast: float
            Contrast of the dots.
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
        self.mask_ramp_prop = mask_ramp_prop

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

        self._inner_mask_active = self.mask_prop[0] is not None
        self._outer_mask_active = self.mask_prop[1] is not None

        self._mask_req = True

    @property
    def mask_ramp_prop(self):
        return self._mask_ramp_prop

    @mask_ramp_prop.setter
    def mask_ramp_prop(self, mask_ramp_prop):
        self._mask_ramp_prop = mask_ramp_prop
        self._mask_req = True

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

        dummy_mask = psychopy.visual.GratingStim(
            win=self._win,
            size=[self.size] * 2,
            tex=np.zeros((2, 2)),
            mask="raisedCos",
            units=self._units
        )

        dummy_mask._calcSizeRendered()

        size_pix = map(int, dummy_mask._sizeRendered)

        if np.mod(size_pix[0], 2) == 1:
            size_pix[0] += 1

        mask_tex = np.zeros(size_pix)

        if self._outer_mask_active:

            outer_mask_tex = psychopy.filters.makeMask(
                matrixSize=size_pix[0],
                shape="raisedCosine",
                radius=self._mask_prop[1],
                fringeWidth=self.mask_ramp_prop[1],
                range=[0, 1]
            )

            mask_tex += outer_mask_tex

        if self._inner_mask_active:

            inner_mask_tex = psychopy.filters.makeMask(
                matrixSize=size_pix[0],
                shape="raisedCosine",
                radius=self._mask_prop[0],
                fringeWidth=self._mask_ramp_prop[0],
                range=[0, 1]
            )

            mask_tex -= inner_mask_tex

        mask_tex[mask_tex > 1] = 1.0
        mask_tex[mask_tex < 0] = 0.0

        mask_tex = (mask_tex * 2.0) - 1.0

        self._mask_tex = mask_tex

        new_mask_tex = stim.utils.pad_image(
            mask_tex,
            pad_value=-1,
            to="pow2+"
        )

        new_size = new_mask_tex.shape[0]

        self._mask = psychopy.visual.GratingStim(
            win=self._win,
            size=[new_size] * 2,
            tex=np.zeros((2, 2)),
            mask=new_mask_tex,
            units="pix"
        )

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

        if self.ori_sigma_deg is not None:
            signal_oris = np.random.normal(
                loc=self.ori_deg,
                scale=self.ori_sigma_deg,
                size=self._n_signal_dipoles
            )
        else:
            signal_oris = np.repeat(
                self.ori_deg,
                repeats=self._n_signal_dipoles
            )

        noise_oris = np.random.uniform(
            low=0.0,
            high=180.0,
            size=self._n_noise_dipoles
        )

        dipole_oris = np.concatenate((signal_oris, noise_oris))

        pole_dist = np.tile(
            (-self._dipole_centre_sep, +self._dipole_centre_sep),
            self._n_dipoles
        )

        if self.ori_type == "trans":

            pole_ori = np.repeat(dipole_oris, repeats=2)

        elif self.ori_type == "polar":

            (theta, _) = psychopy.misc.cart2pol(
                self._dipole_xy[:, 0],
                self._dipole_xy[:, 1]
            )

            theta += dipole_oris

            pole_ori = np.repeat(theta, repeats=2)

        else:
            raise ValueError("Unknown ori_type " + self._ori_type)

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


    def draw(self, ignore_update_error=False):

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

        pyglet.gl.glBlendFunc(
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA,
            pyglet.gl.GL_SRC_ALPHA
        )

        self._mask.draw()

        pyglet.gl.glBlendFunc(
            pyglet.gl.GL_SRC_ALPHA,
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA
        )
