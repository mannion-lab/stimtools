from __future__ import absolute_import, print_function, division

import time

try:
    import parallel
except ImportError:
    pass

try:
    import serial
except ImportError:
    pass


class AudioFileParallel(object):

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


class AudioFileSerial(object):

    def __init__(self, port="/dev/audiofile"):
        """Interface to the CRS 'AudioFile' device.

        Parameters
        ----------
        port: string, optional
            The `port` path, as required by `pyserial`.

        """

        self._device = serial.Serial(port=port)

        self._product_type = self._send_msg("$ProductType")

        if self._product_type != "AudioFile":
            raise OSError("Device doesn't seem to be an AudioFile")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _send_msg(self, message_str, delay=0.1):

        _ = self._device.read(self._device.inWaiting())  # noqa

        if not message_str.endswith("\r"):
            message_str += "\r"

        self._device.write(message_str)

        time.sleep(delay)

        response = self._device.read(self._device.inWaiting())

        if response.startswith("$"):
            response = response.strip().split(";")[1]

        return response

    def close(self):
        """Closes the serial communication channel."""

        self._device.close()

    def playlist(self, playlist):
        """Change to the new playlist file.

        Parameters
        ----------
        playlist: string
            Path to the new playlist file. Must end in '.xml'.

        """

        if not playlist.endswith(".xml"):
            raise ValueError("Playlist needs to end in .xml")

        message = "$playlist=[{p:s}]".format(p=playlist)

        reply = self._send_msg(message_str=message)

        if reply != playlist:
            print("Error setting playlist; response was " + reply)

    def play(self, track_num):
        """Plays a track.

        Parameters
        ----------
        track_num: integer, [1, 499]
            Track number, according to the 'Playlist.xml' register on the
            device.

        """

        if not (1 <= track_num <= 499):
            raise ValueError("Incorrect track number")

        msg = "$starttrack=[{n:d}]".format(n=track_num)

        reply = self._send_msg(msg)

        if reply != str(track_num):
            print("Error playing track; response was " + reply)
