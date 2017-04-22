from __future__ import absolute_import, print_function, division

try:
    import parallel
except ImportError:
    pass


class AudioFile(object):

    def __init__(self, port=None):
        """Interface to the CRS 'AudioFile' device.

        Parameters
        ----------
        port: int or None, optional
            The `port` value, as required by `pyparallel`.

        """

        if port is None:
            port = 0

        self._device = parallel.Parallel(port=port)

    def cue(self, track_num):
        """Prepares a track for presentation.

        Parameters
        ----------
        track_num: integer, [1, 127]
            Track number, according to the 'Playlist.xml' register on the
            device.

        Notes
        -----
        * This automatically resets the trigger bit.

        """

        if not (1 <= track_num <= 127):
            raise ValueError("Incorrect track number")

        self._device.setData(track_num)

    def trigger(self, trigger_val=129):
        """Triggers sound playback.

        Parameters
        ----------
        trigger_val: int, [128, 255], optional
            The trigger is set by any value greater than 128. By specifying an
            appropriate value here, the next track to deliver can be
            automatically cued. The default resets it to track number 1.

        """

        self._device.setData(trigger_val)
