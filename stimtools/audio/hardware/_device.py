
from __future__ import absolute_import, print_function, division

from ._af import (
    AudioFileParallel,
    AudioFileParallelUsingD0,
    AudioFileSerial,
    write_playlist,
    check_audiofile
)

from ._sc import SoundCard


class Player(object):

    def __init__(self, device, **device_args):

        device_table = {
            "af_parallel": AudioFileParallel,
            "af_parallel_d0": AudioFileParallelUsingD0,
            "af_serial": AudioFileSerial,
            "sc": SoundCard,
        }

        self._device_str = device
        self._device_args = device_args

        self.device = device_table[self._device_str](**device_args)

        self.play = self.device.play
        self.stop = self.device.stop
        self.cue = self.device.cue
        self.close = self.device.close

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
