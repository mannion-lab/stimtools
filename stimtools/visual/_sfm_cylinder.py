import numpy as np

try:
    import psychopy.visual
    import psychopy.event
except ImportError:
    pass

import stimtools.utils


def demo():

    with psychopy.visual.Window((512, 512), fullscr=False, units="pix") as win:

        cyl = SFMCylinder(
            win=win,
            size=(300, 200),
            rotation=90.0,
            n_dots=500,
            speed=0.125,
            dot_size=4,
            dot_shape="square",
            lifetime=1.0,
            gen_meth="surface",
        )

        keep_going = True

        while keep_going:

            cyl.draw()
            win.flip()

            cyl.update(1 / 60.0)

            keys = psychopy.event.getKeys()

            for key in keys:

                if key == "space":
                    psychopy.event.waitKeys()

                elif key == "q":
                    keep_going = False


def save_vid(vid_stem, fps=30, loops=5):

    speed = 0.125
    rev_time = 1.0 / speed

    update_inc = 1.0 / fps

    n_frames = int(rev_time * fps * loops)

    caps = np.full((512, 512, n_frames), np.nan, dtype=np.uint8)

    with psychopy.visual.Window((512, 512), fullscr=False, units="pix") as win:

        cyl = SFMCylinder(
            win=win,
            size=(300, 200),
            rotation=90.0,
            n_dots=500,
            speed=0.125,
            dot_size=8,
            lifetime=1.0,
            gen_meth="surface",
        )

        for i_frame in range(n_frames):

            cyl.draw()
            win.flip()

            cap = np.array(win.getMovieFrame())[..., 0]
            win.movieFrames = []

            cap = (cap.astype("float") / 255.0) ** (1.0 / 2.2)

            cap = (cap * 255.0).astype("uint8")

            caps[..., i_frame] = cap

            cyl.update(update_inc)

    stimtools.utils.img_seq_to_vid(
        image_paths=caps,
        vid_stem=vid_stem,
        vid_extensions=["mp4"],
        fps=fps,
        overwrite=True,
    )


class SFMCylinder():
    def __init__(
        self,
        win,
        size=(256, 256),
        speed=1.0,
        n_dots=100,
        rotation=0.0,
        lifetime=np.Inf,
        gen_meth="phase",
        dot_polarities=(-1, +1),
        dot_size=1.0,
        units="pix",
        centre=(0.0, 0.0),
        dot_shape="gauss",
        colour_mask=(1, 1, 1),
        extra_args=None,
    ):
        """Structure-from-motion stimulus.

        Parameters
        ----------
        win : PsychoPy Window instance
            Window to draw to
        size : 2-item list of numbers
            (width, height) of stimulus, prior to any rotation and in ``units``
        speed : float
            Rotation speed, in revolutions per second
        n_dots : integer
            Number of dots
        rotation : float
            Object rotation, in degrees
        lifetime : number or np.Inf
            How long each element 'lives' before being regenerated in a new
            position (in seconds)
        gen_meth : string, {"phase", "surface"}
            Whether to generate starting positions randomly in phase or surface
            space
        dot_polarities : list of floats
            Dot polarities to use.
        dot_size : float
            Size of each element, in ``units``
        units : string
            Stimulus units
        centre : 2-item list of floats
            Centre position of the object
        dot_shape : string, {"gauss", "circle", "square"}
            Shape of each individual element
        colour_mask : three-item array of floats
            Value to apply to the RGB channels prior to drawing.
        extra_args : None or dict
            Any extra parameters that are passed directly to
            ``psychopy.visual.ElementArrayStim``

        """

        self._win = win
        self._size = np.array(size)
        self._speed = speed
        self._n_dots = n_dots
        self._rotation = rotation
        self._lifetime = lifetime
        self._gen_meth = gen_meth
        self._dot_polarities = dot_polarities
        self._dot_size = dot_size
        self._units = units
        self._centre = centre
        self._dot_shape = dot_shape
        self._colour_mask = np.array(colour_mask)

        if extra_args is None:
            self._extra_args = {}
        else:
            self._extra_args = extra_args

        # seed with some initial lifetimes
        if np.isfinite(self._lifetime):
            self._dot_ages = np.random.uniform(
                low=0.0, high=self._lifetime, size=self._n_dots
            )
        else:
            self._dot_ages = np.zeros(self._n_dots)

        # initialise the stimulus
        tex = np.ones([2] * 2)

        if self._dot_shape == "square":
            mask = None
        else:
            mask = self._dot_shape

        # this just sets up the basics - other elements are set when updating
        self._stim = psychopy.visual.ElementArrayStim(
            win=self._win,
            units=self._units,
            fieldPos=self._centre,
            sizes=self._dot_size,
            nElements=self._n_dots,
            elementTex=tex,
            elementMask=mask,
            interpolate=False,
            autoLog=False,
            **self._extra_args
        )

        self._phases = self._gen_phases(n_to_gen=self._n_dots, gen_meth=self._gen_meth)

        self._draw_order = np.random.permutation(self._n_dots)

        self.set_rotation(self._rotation)

        self._colours = np.ones((self._n_dots, 3))

        self._update_count = 0

        self.update(0)

    def update(self, delta_t):

        ph_inc = (delta_t * self._speed) * 2 * np.pi

        self._phases[:, 1] = np.mod(self._phases[:, 1] + ph_inc, 2 * np.pi)

        if self._update_count >= 2:
            self._dot_ages += delta_t

        dot_is_dead = self._dot_ages > self._lifetime

        n_dead_dots = np.sum(dot_is_dead)

        new_phases = self._gen_phases(n_to_gen=n_dead_dots, gen_meth=self._gen_meth)

        self._dot_ages[dot_is_dead] = 0

        self._phases[dot_is_dead, :] = new_phases

        norm_xy = np.vstack([self._phases[:, 0], np.cos(self._phases[:, 1])]).T

        # those with a colour update required
        colour_update = dot_is_dead

        if self._update_count == 0:
            colour_update = [True] * self._n_dots
            self._first_update = False

        # set the colours
        if np.sum(colour_update) > 0:
            self._set_colours(colour_update)

        norm_xy = norm_xy[self._draw_order, :]
        self._dot_cols = self._colours[self._draw_order, :]

        self._dot_cols_masked = self._dot_cols * self._colour_mask

        xy = norm_xy * (self._size / 2.0)

        if self._xform.ndim == 3:
            for i_d in range(self._n_dots):
                xy[i_d, :] = np.dot(xy[i_d, :], self._xform[..., i_d])
        else:
            xy = np.dot(xy, self._xform)

        self._stim.setXYs(xy)
        self._stim.setColors(self._dot_cols_masked)

        self._update_count += 1

    def set_rotation(self, rotation):

        self._rotation = rotation

        self._xform = self._get_xform()

    def set_contrast(self, contrast):

        self._stim.setContrs(contrast)

    def set_pos(self, pos):

        self._stim.setFieldPos(pos)

    def set_opacities(self, opacities):

        self._stim.setOpacities(opacities)

    def set_colour_mask(self, colour_mask):

        self._colour_mask = colour_mask

        self._dot_cols_masked = self._dot_cols * self._colour_mask

        self._stim.setColors(self._dot_cols_masked)

    def draw(self):

        self._stim.draw()

    def _set_colours(self, colour_update):

        i_update = np.where(colour_update)[0]

        new_colours = np.random.choice(self._dot_polarities, len(i_update))

        for (i_dot, c) in zip(i_update, new_colours):
            self._colours[i_dot, :] = c

    def _get_xform(self, rotation=None):

        if rotation is None:
            rotation = self._rotation

        xform = np.array(
            [
                [+np.cos(np.radians(rotation)), -np.sin(np.radians(rotation))],
                [+np.sin(np.radians(rotation)), +np.cos(np.radians(rotation))],
            ]
        )

        return xform


def gen_phases(n_to_gen, gen_meth):

    phases = np.empty((n_to_gen, 2))
    phases.fill(np.NAN)

    phases[:, 0] = np.random.uniform(low=-1.0, high=1.0, size=n_to_gen)

    # if generation method is by phase, its simple
    if gen_meth == "phase":
        phases[:, 1] = np.random.uniform(low=0.0, high=2 * np.pi, size=n_to_gen)

    # if by surface, its only slightly less simple
    elif gen_meth == "surface":

        dir_n = n_to_gen / 2.0

        # this is only useful when ``n_to_gen`` is odd, but doesn't hurt in
        # the case where it is even
        dir_n = [np.ceil(dir_n), np.floor(dir_n)]

        dir_phases = []

        for (n, phase_offset) in zip(dir_n, (0, np.pi)):

            n = int(n)

            surf_pos = np.random.uniform(low=-1.0, high=+1.0, size=n)

            dir_phase = np.arccos(surf_pos)

            dir_phase += phase_offset

            dir_phases.append(dir_phase)

        phases[:, 1] = np.hstack(dir_phases)

        # shuffle to get rid of the structure
        phases[:, 1] = phases[np.random.permutation(phases.shape[0]), 1]

    else:
        raise ValueError("Unknown generation method " + gen_meth)

    assert np.sum(np.isnan(phases)) == 0

    return phases


if __name__ == "__main__":
    demo()
