from __future__ import absolute_import, print_function, division

import psychopy.visual
import psychopy.misc
import psychopy.visual.filters


class Fixation(object):

    def __init__(
        self,
        win,
        outer_diam_pix,
        inner_diam_pix,
        bg_colour=(-1, -1, -1),
        line_colour=(+1, +1, +1),
        spot_colour=(-1, -1, -1),
        circle_edges=128
    ):
        """
        Constructs a fixation target like what is recommended by Thaler et al.
        (2013), Vision Research.

        Parameters
        ----------
        win: window instance
            PsychoPy window.
        outer_diam_pix: float
            Diameter of the outer circle. Thaler et al. use 0.6 dva.
        inner_diam_pix: float
            Diameter of the inner circle. Thaler et al. use 0.2 dva.
        bg_colour: three-item sequence of floats
            RGB colour of the background circle. Settable.
        line_colour: three-item sequence of floats
            RGB colour of the crosshairs. Settable.
        spot_colour: three-item sequence of floats
            RGB colour of the central spot. Settable.
        circle_edges: int
            How many vertices to a circle.

        """

        self._win = win
        self._outer_diam_pix = outer_diam_pix
        self._inner_diam_pix = inner_diam_pix
        self._circle_edges = circle_edges
        self._stim = {}

        self._stim["bg"] = psychopy.visual.Circle(
            win=self._win,
            radius=self._outer_diam_pix / 2.0,
            units="pix",
            lineColor=bg_colour,
            fillColor=bg_colour,
            edges=self._circle_edges
        )

        self._stim["h_line"] = psychopy.visual.Line(
            win=self._win,
            start=[-self._outer_diam_pix / 2.0, 0],
            end=[+self._outer_diam_pix / 2.0, 0],
            lineColor=line_colour,
            units="pix",
            lineWidth=self._inner_diam_pix
        )
        self._stim["v_line"] = psychopy.visual.Line(
            win=self._win,
            start=[0, -self._outer_diam_pix / 2.0],
            end=[0, +self._outer_diam_pix / 2.0],
            lineColor=line_colour,
            units="pix",
            lineWidth=self._inner_diam_pix
        )

        self._stim["spot"] = psychopy.visual.Circle(
            win=self._win,
            radius=self._inner_diam_pix / 2.0,
            units="pix",
            lineColor=spot_colour,
            fillColor=spot_colour,
            edges=self._circle_edges
        )

        self.bg_colour = bg_colour
        self.line_colour = line_colour
        self.spot_colour = spot_colour


    @property
    def bg_colour(self):
        return self._bg_colour

    @bg_colour.setter
    def bg_colour(self, bg_colour):
        self._bg_colour = bg_colour

        self._stim["bg"].lineColor = bg_colour
        self._stim["bg"].fillColor = bg_colour

    @property
    def line_colour(self):
        return self._line_colour

    @line_colour.setter
    def line_colour(self, line_colour):
        self._line_colour = line_colour

        self._stim["h_line"].lineColor = line_colour
        self._stim["v_line"].fillColor = line_colour

    @property
    def spot_colour(self):
        return self._spot_colour

    @spot_colour.setter
    def spot_colour(self, spot_colour):
        self._spot_colour = spot_colour

        self._stim["spot"].lineColor = spot_colour
        self._stim["spot"].fillColor = spot_colour

    def draw(self, contrast=1):

        if contrast == 1:
            stim_c = (
                ("bg", -1),
                ("h_line", 1),
                ("v_line", 1),
                ("spot", -1)
            )
        elif contrast == -1:

            stim_c = (
                ("bg", 1),
                ("h_line", -1),
                ("v_line", -1),
                ("spot", 1)
            )

        for (stim_type, stim_contrast) in stim_c:
            self._stim[stim_type].lineColor = stim_contrast
            self._stim[stim_type].fillColor = stim_contrast

            self._stim[stim_type].draw()

