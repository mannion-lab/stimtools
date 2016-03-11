
# UNFINISHED
#  - use properties
#  - general cleanup
#  - get rid of mask stuff

from __future__ import absolute_import, print_function, division

import numpy as np

import psychopy.visual
import psychopy.misc


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
        mask_ramp_prop=(None, 0.1),
        contrast=1.0,
        dot_sep_tol=3.0,
        max_iterations=10000
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
        dot_sep_tol: float
            Tolerance for dot positioning. Dots will not be allowed to be
            positioned closer than `dot_size` * `dot_sep_tol` from any other
            dots.
        max_iterations: int
            Maximum number of iterations when calcuating the random dot
            positions. If this is exceeded, an error is raised.

        """

        self._win = win

        self._stim = psychopy.visual.ElementArrayStim(
            win=self._win,
            autoLog=False,
            elementTex=None
        )

        self.size = size
        self.n_dipoles = n_dipoles
        self.dipole_sep = dipole_sep
        self.dot_size = dot_size
        self.ori_type = ori_type
        self.ori_deg = ori_deg
        self.ori_sigma_deg = ori_sigma_deg
        self.coh = coh
        self.col_set = col_set
        self.pos = pos
        self.dot_type = dot_type
        self.mask_prop = mask_prop
        self.mask_ramp_prop = mask_ramp_prop
        self.contrast = contrast
        self.dot_sep_tol = dot_sep_tol
        self.max_iterations = max_iterations

        self._distribute_req = True
        self._mask_req = True


    @property
    def _half_size(self):
        return self._size / 2.0

    @property
    def _n_dots(self):
        return self._n_dipoles * 2

    @property
    def _n_dipole_types(self):

        n_signal = int(self.n_dipoles * self.coh)
        n_noise = self.n_dipoles - n_signal

        return (n_signal, n_noise)

    @property
    def _n_signal_dipoles(self):
        return self._n_dipole_types[0]

    @property
    def _n_noise_dipoles(self):
        return self._n_dipole_types[1]

    @property
    def update_req(self):
        return self._distribute_req or self._mask_req

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
        self._distribute_req = True

    @property
    def n_dipoles(self):
        return self._n_dipoles

    @n_dipoles.setter
    def n_dipoles(self, n_dipoles):
        self._n_dipoles = n_dipoles
        self._distribute_req = True

    @property
    def dipole_sep(self):
        return self._dipole_sep

    @dipole_sep.setter
    def dipole_sep(self, dipole_sep):
        self._dipole_sep = dipole_sep
        self._distribute_req = True

    @property
    def dot_size(self):
        return self._dot_size

    @dot_size.setter
    def dot_size(self, dot_size):
        self._dot_size = dot_size
        self._distribute_req = True

    @property
    def coh(self):
        return self._coh

    @coh.setter
    def coh(self, coh):
        self._coh = coh
        self._instance_req = True

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

        self._mask_req = True

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
    def mask_ramp_prop(self):
        return self._mask_ramp_prop

    @mask_ramp_prop.setter
    def mask_ramp_prop(self, mask_ramp_prop):
        self._mask_ramp_prop = mask_ramp_prop
        self._mask_req = True

    @property
    def contrast(self):
        """Some help"""
        return self._contrast

    @contrast.setter
    def contrast(self, contrast):
        self._contrast = contrast
        self._mask_req = True

    @property
    def dot_sep_tol(self):
        return self._dot_sep_tol

    @dot_sep_tol.setter
    def dot_sep_tol(self, dot_sep_tol):
        self._dot_sep_tol = dot_sep_tol
        self._min_dot_sep = self.dot_size * self.dot_sep_tol
        self._distribute_req = True

    def distribute(self):

        iterations = 0

        while iterations < self.max_iterations:

            self._dipole_xy = np.empty((self.n_dipoles, 2))
            self._dipole_xy.fill(np.NAN)

            self._dot_xy = np.empty((self._n_dots, 2))
            self._dot_xy.fill(np.NAN)

            for i_dipole in xrange(self.n_dipoles):

                i_dot_base = i_dipole * 2

                dipole_iterations = 0

                while dipole_iterations < self.max_iterations:

                    # generate a proposed dipole xy pair
                    p_dipole_xy = np.random.uniform(
                        low=-self._half_size,
                        high=+self._half_size,
                        size=2
                    )

                    # determine the orientation of the dipole
                    if i_dipole < self._n_signal_dipoles:
                        ori = self.ori_deg
                    else:
                        ori = np.random.uniform(0.0, 180.0)

                    # now need to position the dipole dots
                    if self.ori_type == "trans":
                        dipole_ori = ori

                    elif self.ori_type == "polar":
                        (dipole_ori, _) = psychopy.misc.cart2pol(p_dipole_xy)

                    p_dot_xy = np.empty((2, 2))
                    p_dot_xy.fill(np.NAN)

                    for (i_dot, dot_offset) in enumerate((-1, +1)):

                        p_dot_xy[i_dot, :] = psychopy.misc.pol2cart(
                            dipole_ori,
                            self._dipole_centre_sep * dot_offset
                        )

                    dist = [
                        np.sqrt(
                            np.sum(
                                (self._dot_xy - p_dot_xy[i_dot, :]) ** 2
                            )
                        )
                        for i_dot in xrange(2)
                    ]

                    if np.logical_or(
                        np.all(np.isnan(dist)),
                        np.all(dist > self._min_dot_sep)
                    ):
                        print( dist)

                        self._dipole_xy[i_dipole, :] = p_dipole_xy
                        self._dot_xy[i_dot_base:i_dot_base + 2, :] = p_dot_xy

                        break

                    dipole_iterations += 1

                # haven't broken out of the dipole iterations, break out of the
                # pattern iterations
                else:
                    break

            # if haven't broken out of the dipole loop, then all good and can
            # break
            else:
                break

            iterations += 1

        # if haven't broken out of the pattern loop, then throw an error
        else:
            raise ValueError("Too many iterations")



    def draw(self, ignore_update_error=False):

        if self._instance_req and not ignore_update_error:
            raise ValueError(
                "Trying to draw a Glass pattern without creating a new " +
                "instance after a setting change"
            )
