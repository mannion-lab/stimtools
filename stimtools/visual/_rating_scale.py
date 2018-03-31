
import numpy as np

import psychopy.visual

import stimtools.utils


class RatingScale(object):

    def __init__(
        self,
        win,
        intervals=(-1, 1),
        initial=0.5,
        scale_width=200,
        scale_height=10,
        scale_colour=(-0.5, ) * 3,
        marker_diam=24,
        marker_colour=(0.5, ) * 3,
        marker_opacity=0.5,
        pos=(0, 0),
        units="pix"
    ):

        self._win = win
        self._intervals = intervals
        self._scale_width = scale_width
        self._scale_height = scale_height
        self._marker_diam = marker_diam
        self._marker_colour = marker_colour
        self._marker_opacity = marker_opacity
        self._pos = pos
        self._scale_colour = scale_colour

        self._initial_value = initial

        self._h_extents = (
            self._pos[0] - self._scale_width / 2.0,
            self._pos[0] + self._scale_width / 2.0
        )

        self._v_extents = (
            self._pos[1] - self._marker_diam / 2.0,
            self._pos[1] + self._marker_diam / 2.0
        )

        self._marker_value = initial

        self._bar = psychopy.visual.Rect(
            win=self._win,
            width=self._scale_width,
            fillColor=self._scale_colour,
            lineColor=None,
            height=self._scale_height,
            units=units,
            pos=pos,
            autoLog=False
        )

        self._marker = psychopy.visual.Circle(
            win=self._win,
            radius=self._marker_diam / 2.0,
            fillColor=self._marker_colour,
            lineColor=None,
            opacity=self._marker_opacity,
            units=units
        )

        self.value = initial
        self._marker.pos = self.val_to_pos(initial)

    def reset(self):

        self.value = self._initial_value
        self._marker.pos = self.val_to_pos(self.value)

    def val_to_pos(self, val):

        prop = stimtools.utils.interval_convert(
            val,
            self._intervals,
            [0.0, 1.0]
        )

        h_offset = prop * self._scale_width

        h_pos = h_offset + self._h_extents[0]

        return (h_pos, self._pos[1])

    def pos_to_val(self, pos):

        val = stimtools.utils.interval_convert(
            pos[0],
            self._h_extents,
            self._intervals
        )

        val = np.clip(val, *self._intervals)

        return val

    def update(self, mouse_pos):

        if self._v_extents[0] < mouse_pos[1] < self._v_extents[1]:
            mouse_pos[1] = self._pos[1]
            mouse_pos[0] = np.clip(
                mouse_pos[0],
                a_min=self._h_extents[0],
                a_max=self._h_extents[1]
            )
            self._marker.pos = mouse_pos

        self.value = self.pos_to_val(self._marker.pos)

    def draw(self):

        self._bar.draw()
        self._marker.draw()


def demo():

    import psychopy.event

    with psychopy.visual.Window((400, 400), fullscr=False, units="pix") as win:

        mouse = psychopy.event.Mouse(win=win)

        rs = RatingScale(win=win, pos=(50, 50))

        keep_going = True

        while keep_going:

            rs.draw()
            win.flip()

            keys = psychopy.event.getKeys()

            keep_going = len(keys) == 0

            if any(mouse.getPressed()):
                rs.update(mouse.getPos())


if __name__ == "__main__":
    demo()
