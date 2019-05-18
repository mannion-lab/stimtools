from .af import AudioFileParallel, AudioFileParallelUsingD0, AudioFileSerial

from ._sc import SoundCard


class Player:
    def __init__(self, interface, **interface_args):

        interface_table = {
            "af_parallel": AudioFileParallel,
            "af_parallel_d0": AudioFileParallelUsingD0,
            "af_serial": AudioFileSerial,
            "sc": SoundCard,
            "dummy": Dummy,
        }

        self._interface_str = interface
        self._interface_args = interface_args

        self.interface = interface_table[self._interface_str](**interface_args)

        self.play = self.interface.play
        self.stop = self.interface.stop
        self.cue = self.interface.cue
        self.close = self.interface.close
        self.start = self.interface.start

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()


class Dummy:
    def __init__(self):

        self.start = self.close = self.play = self.stop

    def cue(self, track_num):
        pass

    def stop(self):
        pass
