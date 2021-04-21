try:
    import psychopy.visual
    import psychopy.misc
except ImportError:
    pass


class Fixation:
    def __init__(
        self,
        win,
        outer_diam_pix,
        inner_diam_pix,
        bg_colour=(-1, -1, -1),
        line_colour=(+1, +1, +1),
        spot_colour=(-1, -1, -1),
        circle_edges=128,
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

        self._stim["aperture"] = psychopy.visual.Aperture(
            win=win,
            size=self._outer_diam_pix,
            nVert=self._circle_edges,
            shape="circle",
            units="pix",
            autoLog=False,
        )

        self._stim["aperture"].enabled = False

        self._stim["bg"] = psychopy.visual.Circle(
            win=self._win,
            radius=self._outer_diam_pix / 2.0,
            units="pix",
            lineColor=None,
            fillColor=bg_colour,
            edges=self._circle_edges,
            autoLog=False,
        )

        self._stim["line"] = psychopy.visual.Rect(
            win=self._win,
            size=(self._outer_diam_pix * 2, self._inner_diam_pix),
            units="pix",
            lineWidth=0,
            lineColor=None,
            fillColor=line_colour,
            autoLog=False,
        )

        self._stim["spot"] = psychopy.visual.Circle(
            win=self._win,
            radius=self._inner_diam_pix / 2.0,
            units="pix",
            fillColor=spot_colour,
            edges=self._circle_edges,
            lineWidth=0,
            autoLog=False,
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

        self._stim["line"].lineColor = line_colour

    @property
    def spot_colour(self):
        return self._spot_colour

    @spot_colour.setter
    def spot_colour(self, spot_colour):
        self._spot_colour = spot_colour

        self._stim["spot"].lineColor = spot_colour
        self._stim["spot"].fillColor = spot_colour

    def draw(self):

        self._stim["aperture"].enabled = True

        self._stim["bg"].draw()
        self._stim["line"].draw()
        self._stim["line"].ori += 90
        self._stim["line"].draw()
        self._stim["spot"].draw()

        self._stim["aperture"].enabled = False
