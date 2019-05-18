import alsaaudio


class Mixer():
    def __init__(self, control="Master", **kwargs):

        self._mixer = alsaaudio.Mixer(control=control, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self._mixer.close()

    @property
    def volume(self):
        return self._mixer.getvolume()

    @volume.setter
    def volume(self, volume):
        self._mixer.setvolume(volume)
