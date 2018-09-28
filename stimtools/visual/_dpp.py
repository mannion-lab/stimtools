
from __future__ import print_function

import pyglet.canvas

try:

    import pyglet.gl

    import psychopy.visual
    import psychopy.hardware.crs

except (ImportError, pyglet.canvas.xlib.NoSuchDisplayException):
    pass


try:
    parent = psychopy.visual.Window
except NameError:
    parent = object


class DisplayPlusPlus(parent):

    def __init__(
        self,
        dpp_mode="mono++",
        dpp_port="/dev/dpp",
        **kwargs
    ):

        super(DisplayPlusPlus, self).__init__(**kwargs)

        self._win_close = super(DisplayPlusPlus, self).close

        self._bits = psychopy.hardware.crs.BitsSharp(
            win=self,
            mode="mono++",
            gamma="hardware",
            portName=dpp_port
        )

        if not hasattr(self._bits, "info"):
            self._win_close()
            raise ValueError("Cannot communicate with the DPP")

        self._bits.temporalDithering = False

        if dpp_mode == "mono++":
            pyglet.gl.glColorMask(1, 1, 0, 1)

    def close(self):

        self._bits.mode = "auto++"
        self._bits.com.close()

        self._win_close()
