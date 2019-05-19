from __future__ import print_function

import numpy as np

import sounddevice


class SoundCard:
    def __init__(self, **extra_settings):

        self._waveform = np.zeros(0)

        self._stream = sounddevice.OutputStream(channels=2, **extra_settings)

        self._status = None

        self._stream.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def cue(self, waveform):

        if waveform.ndim != 2:
            waveform = np.repeat(waveform[:, np.newaxis], 2, axis=1)

        if waveform.dtype != np.float32:
            waveform = waveform.astype("float32")

        self._cued_waveform = waveform

    def play(self, waveform=None, decue=True):

        if waveform is not None:
            self.cue(waveform=waveform)

        if self._cued_waveform is None:
            raise ValueError("Haven't cued a waveform")

        self._stream.write(data=self._cued_waveform)

        if decue:
            self._cued_waveform = None

    def stop(self):
        self._stream.stop()

    def start(self):
        self.errors = 0
        self._stream.start()

    def close(self):
        self._stream.close()
