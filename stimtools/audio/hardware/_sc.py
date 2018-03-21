
import numpy as np

import sounddevice


class SoundCard(object):

    def __init__(
        self,
        **extra_settings
    ):

        self._stream = sounddevice.OutputStream(
            callback=self._callback,
            **extra_settings
        )

        self._stream.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _callback(indata, outdata, frames, time, status):
        outdata[:] = (np.random.uniform(-1,1,outdata.shape).astype("float32"))

    def cue(self, waveform):
        self._cued_waveform = waveform

    def play(self):

        if self._cued_waveform is None:
            raise ValueError("Attempted to play but no waveform was cued")

        self._stream.write(self._cued_waveform)

        self._cued_waveform = None

    def stop(self):
        self._stream.stop()

    def close(self):
        self._stream.close()
