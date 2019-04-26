
from __future__ import print_function

import pyglet.canvas

try:

    import pyglet.gl

    import psychopy.visual
    import psychopy.hardware.crs

except pyglet.canvas.xlib.NoSuchDisplayException:
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

        # requires FBO
        kwargs["useFBO"] = True
        # needed to get correct refresh
        kwargs["waitBlanking"] = False
        # gamma is always 1.0
        kwargs["gamma"] = 1.0

        super(DisplayPlusPlus, self).__init__(**kwargs)

        self._win_close = super(DisplayPlusPlus, self).close

        try:
            self._bits = psychopy.hardware.crs.BitsSharp(
                win=self,
                mode=dpp_mode,
                gamma="hardware",
                portName=dpp_port
            )

        except (pyglet.gl.GLException, IndexError):
            self.close()
            raise

        if not hasattr(self._bits, "info"):
            self._win_close()
            raise ValueError("Cannot communicate with the DPP")

        # using self._bits.temporalDithering leaves the serial device in a bad
        # state
        self._bits.sendMessage("TemporalDithering=[OFF]\r")
        self._bits.pause()
        self._bits.getResponse()

    def close(self):

        if hasattr(self, "_bits"):
            self._bits.mode = "auto++"
            self._bits.com.close()

        self._win_close()
