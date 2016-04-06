from __future__ import absolute_import, print_function, division

import numpy as np

import psychopy.visual
import psychopy.event

import stim.utils

class SFMCylinder(object):

    def __init__(
        self,
        win,
        size,
        location,
        rotation,
        n_dots,
        dot_size,
        dot_lifetime_ms,
        rev_per_s,
        phase_meth="screen",
        dot_shape="gauss",
        dot_polarity=+1,
        units="pix"
    ):
        """
        Structure-from-motion cylinder.

        Parameters
        ----------
        win: window instance
            PsychoPy window.
        size: two-item list of numbers
            Width and height of the cylinder, in `units`.
        location: two-item list of numbers
            Screen location, in `units`.
        rotation: float
            Cylinder rotation, in degrees. Zero is rotation about a horizontal
            axis.
        n_dots: int
            Number of total dots in the cylinder.
        dot_size: number
            Size of each dot, in `units`.
        dot_lifetime_ms: float or np.Inf
            How long each dot 'survives' before being regenerated.
        rev_per_s: float
            Number of complete revolutions per second.
        phase_meth: string, {"screen", "surface"}, optional
            How to generate the phases; either in screen or surface
            coordinates.
        dot_shape: string, optional
            Shape of each dot, in PsychoPy format.
        dot_polarity: float, optional
            Contrast polarity of each dot.
        units: string, optional
            Format of the parameters, in PsychoPy format.

        """

        self._win = win
        self._size = np.array(size)
        self._location = np.array(location)
        self._rotation = rotation
        self._n_dots = n_dots
        self._dot_size = dot_size
        self._dot_lifetime_ms = dot_lifetime_ms
        self._dot_polarity = dot_polarity
        self._dot_shape = dot_shape
        self._phase_meth = phase_meth
        self._rev_per_s = rev_per_s
        self._units = units

        if np.isinf(self._dot_lifetime_ms):
            self._dot_age_ms = np.ones(self._n_dots) * np.Inf

        else:
            # seed some initial dot ages
            self._dot_age_ms = np.random.uniform(
                low=0.0,
                high=self._dot_lifetime_ms,
                size=self._n_dots
            )

        # initialise the basic stimulus
        self._stim = psychopy.visual.ElementArrayStim(
            win=self._win,
            sizes=self._dot_size,
            fieldPos=self._location,
            nElements=self._n_dots,
            elementTex=np.ones((2, 2)),
            elementMask=self._dot_shape,
            autoLog=False,
            contrs=self._dot_polarity,
            units=self._units
        )

        # create the initial phase structure
        self._phases = gen_phases(self._n_dots, self._phase_meth)

        self._timer_s = 0.0

        self._xform = get_xform(self._rotation)


    def update(self, delta_t_s):

        # increment the age of the dots
        self._dot_age_ms += (delta_t_s * 1000)

        # find out which dots have 'died' of old age
        dead_dots = (self._dot_age_ms > self._dot_lifetime_ms)
        n_dead_dots = np.sum(dead_dots)

        # regenerate the phases of those dots that have passed on
        self._phases[dead_dots, :] = gen_phases(n_dead_dots, self._phase_meth)
        self._dot_age_ms[dead_dots] = 0

        # update the running timer (not just delta)
        self._timer_s += delta_t_s

        # work out how much the phase should have changed on this frame, based
        # on how much time has elapsed
        delta_phase = (delta_t_s * self._rev_per_s) * 2 * np.pi

        # update the phase along the modulated axis
        self._phases[:, 1] += delta_phase
        self._phases[:, 1] = np.mod(self._phases[:, 1], 2 * np.pi)

        # now, we want to converted the modulated axis from angular to
        # normalised units
        self._norm_xy = np.copy(self._phases)
        self._norm_xy[:, 1] = np.cos(self._norm_xy[:, 1])

        # finally, we convert to screen coordinates by applying the rotation
        # transform and scaling
        self._screen_xy = (
            np.dot(self._norm_xy, self._xform) *
            (self._size / 2.0)
        )

        # and update the dot positions for the psychopy stimulus
        self._stim.setXYs(self._screen_xy)


    def draw(self):

        self._stim.draw()


class SFMCylinderRocking(SFMCylinder):

    def __init__(self, *args, **kwargs):

        super(SFMCylinderRocking, self).__init__(*args, **kwargs)


def gen_phases(n_to_gen, phase_meth):

    if phase_meth == "screen":

        phases = np.random.uniform(
            low=-1,
            high=+1,
            size=(n_to_gen, 2)
        )

        phases[:, 1] = np.arccos(phases[:, 1])

        phase_offset = np.random.choice(
            a=(0, np.pi),
            size=n_to_gen
        )

        phases[:, 1] += phase_offset

    elif phase_meth == "surface":

        phases = np.random.uniform(
            low=0.0,
            high=2 * np.pi,
            size=(n_to_gen, 1)
        )

        pos = np.random.uniform(
            low=-1.0,
            high=1.0,
            size=(n_to_gen, 1)
        )

        phases = np.hstack((pos, phases))

    return phases


def get_xform(rotation_deg):

    rotation = np.radians(rotation_deg)

    xform = np.array(
        [
            [+np.cos(rotation), -np.sin(rotation)],
            [+np.sin(rotation), +np.cos(rotation)]
        ]
    )

    return xform

