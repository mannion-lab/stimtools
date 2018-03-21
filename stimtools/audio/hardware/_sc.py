
import numpy as np

import sounddevice


class SoundCard(object):

    def __init__(
        self,
        **extra_settings
    ):

        self._waveform = np.zeros(0)

        self._stream = sounddevice.OutputStream(
            callback=self._callback,
            channels=2,
            **extra_settings
        )

        self._stream.start()

    def _callback(self, outdata, frames, time, status):

        if status:
            print(status)

        if len(self._waveform) == 0:
           outdata.fill(0.0)

        else:

            if self._waveform.shape[0] < frames:
                waveform = np.zeros(
                    (frames, 2),
                    dtype=self._waveform.dtype
                )
                waveform[:self._waveform.shape[0], :] = self._waveform
                self._waveform = waveform

            outdata[:] = self._waveform[:frames, :]
            self._waveform = self._waveform[frames:, :]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def cue(self, waveform):

        if waveform.ndim != 2:
            waveform = np.repeat(
                waveform[:, np.newaxis],
                (1, 2)
            )

        if waveform.dtype != np.float32:
            waveform = waveform.astype("float32")

        self._cued_waveform = waveform

    def play(self):

        self._waveform = self._cued_waveform


    def stop(self):
        self._stream.stop()

    def close(self):
        self._stream.close()
