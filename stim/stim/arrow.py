
import psychopy.visual


class Arrow(object):

    def __init__(
        self,
        win,
        extra_args=None
    ):

        if extra_args is None:
            extra_args = {}

        self._win = win

        vertices = (
            (
                (-1, 0.1),
                (0.7, 0.1),
                (0.7, 0.2),
                (1.0, 0.0),
                (0.7, -0.2),
                (0.7, -0.1),
                (-1, -0.1)
            )
        )

        self._arrow = psychopy.visual.ShapeStim(
            win=win,
            units="norm",
            vertices=vertices,
            **extra_args
        )

    def __setattr__(self, name, value):
        """This is pretty hacky but works!"""

        if name in ["_win", "_arrow"]:
            self.__dict__[name] = value

        else:
            setattr(self._arrow, name, value)

    def draw(self):
        self._arrow.draw()
