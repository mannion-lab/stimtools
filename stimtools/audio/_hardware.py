from __future__ import absolute_import, print_function, division

import os
import time
import xml.etree.ElementTree as etree
import xml.dom.minidom

try:
    import parallel
except ImportError:
    parallel_imported = False
else:
    parallel_imported = True

try:
    import serial
except ImportError:
    serial_imported = False
else:
    serial_imported = True


class AudioFileParallelUsingD0(object):

    def __init__(self, port=None):
        """Interface to the CRS 'AudioFile' device, when the option in the
        playlist file ''UseDigitalInputD0'' is set to TRUE. This allows for
        tracks from 1 to 255, whereas otherwise it is from 1 to 128.

        Parameters
        ----------
        port: int or None, optional
            The `port` value, as required by `pyparallel`.

        """

        if not parallel_imported:
            raise ImportError("Could not import pyparallel")

        if port is None:
            port = 0

        self._device = parallel.Parallel(port=port)

    def _track_to_pins(self, track_num, set_trigger=False):
        """Converts a desired track number and trigger status to the pin
        settings for the 'data' and 'strobe' lines.

        Parameters
        ----------
        track_num: integer, [1, 256]
            Track number, according to the 'Playlist.xml' register on the
            device.
        set_trigger: bool, optional
            Whether the trigger bit should be set or not.

        Returns
        -------
        (data_val, strobe_val): integers
            Values to send to the data and strobe lines.

        """

        if not (0 <= track_num <= 256):
            raise ValueError("Incorrect track number")

        track_binary = "{n:08b}".format(n=track_num)

        data_line = (
            str(int(set_trigger)) +  # trigger bit
            track_binary[:-1]
        )

        data_val = int(data_line, 2)

        strobe_val = int(track_binary[-1])

        return (data_val, strobe_val)

    def cue(self, track_num):
        """Prepares a track for presentation.

        Parameters
        ----------
        track_num: integer, [1, 256]
            Track number, according to the 'Playlist.xml' register on the
            device.

        Notes
        -----
        * This automatically resets the trigger bit.

        """

        (data_val, strobe_val) = self._track_to_pins(track_num=track_num)

        self._device.setData(data_val)
        self._device.setDataStrobe(strobe_val)

    def trigger(self):
        """Triggers sound playback and resets all pins."""

        self._device.setDataStrobe(0)
        self._device.setData(128)


class AudioFileParallel(object):

    def __init__(self, port=None):
        """Interface to the CRS 'AudioFile' device.

        Parameters
        ----------
        port: int or None, optional
            The `port` value, as required by `pyparallel`.

        """

        if not parallel_imported:
            raise ImportError("Could not import pyparallel")

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

        if not parallel_imported:
            raise ImportError("Could not import pyserial")

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

    def stop(self):
        """Stops the device from playing"""
        self._send_msg(message_str="$Stoptrack")

    def reboot(self):
        """Reboots the device"""

        self._send_msg(message_str="$debug")

    def close(self):
        """Closes the serial communication channel."""

        self._device.close()

    @property
    def playlist(self):

        return self._send_msg(
            message_str="$playlist",
            delay=0.1
        )

    @playlist.setter
    def playlist(self, new_playlist):

        max_wait = 180.0

        if not new_playlist.endswith(".xml"):
            raise ValueError("Playlist needs to end in .xml")

        if (self.playlist != new_playlist):

            start_time = time.clock()

            message = "$playlist=[{p:s}]".format(p=new_playlist)

            reply = self._send_msg(message_str=message, delay=1.0)

            status_ok = (reply == new_playlist)

            while (not status_ok) and (time.clock() - start_time) < max_wait:

                reply = self.playlist

                if reply == new_playlist:
                    break

            else:
                print("Unable to set playlist")

    def play(self, track_num, delay=0.1):
        """Plays a track.

        Parameters
        ----------
        track_num: integer, [1, 499]
            Track number, according to the active playlist on the
            device.

        """

        if not (1 <= track_num <= 499):
            raise ValueError("Incorrect track number")

        msg = "$starttrack=[{n:d}]".format(n=track_num)

        reply = self._send_msg(msg, delay=delay)

        if reply != str(track_num):
            print("Error playing track; response was " + reply)


def write_playlist(
    playlist_path,
    wav_folder,
    entries,
    swap_channels=False,
    use_D0=True
):
    """Writes an audiofile XML playlist file.

    Parameters
    ----------
    playlist_path: string
        Location to write the playlist.
    wav_folder: string
        The relative path to the directory containing the wav files on the
        device.
    entries: dict
        Keys are integers and values are the associated wav file paths.
    swap_channels: bool, optional
        Whether to include a flag in the XML to swap the channels on the
        device.
    use_D0: bool, optional
        Whether to include a flag in the XML to indicate the use of the first
        parallel port pin.

    """

    base = etree.Element("AUDIOFILE_PLAYLIST")

    playlist = etree.SubElement(base, "PLAYLIST1")

    etree.SubElement(playlist, "Entry", Folder=wav_folder)

    keys = sorted(entries)

    for key in keys:

        key_code = "Code{n:03d}".format(n=key)

        etree.SubElement(
            playlist,
            "Entry",
            **{key_code: entries[key]}
        )

    system = etree.SubElement(base, "SYSTEM")

    use_D0 = str(use_D0).upper()

    etree.SubElement(system, "Entry", UseDigitalInputD0=use_D0)
    etree.SubElement(system, "Entry", StopCode="0")
    etree.SubElement(system, "Entry", SwapChannels=str(swap_channels).upper())
    etree.SubElement(system, "Entry", SDRAMTest="FALSE")

    rough_string = etree.tostring(base)
    reparsed = xml.dom.minidom.parseString(rough_string)

    reparsed_pretty = reparsed.toprettyxml(indent=" " * 4)

    with open(playlist_path, "w") as playlist_file:
        playlist_file.write(reparsed_pretty)


def check_audiofile(mount_expected):
    """Checks the details of the AudioFile.

    Parameters
    ----------
    mount_expected: bool
        Whether the AudioFile is expected to be mounted or not.

    """

    try:
        audiofile_path = os.environ["AUDIOFILE_PATH"]
    except KeyError:
        raise ValueError(
            "The environmental variable AUDIOFILE_PATH has not been set"
        )

    mounted = os.path.ismount(audiofile_path)

    if (not mounted) and mount_expected:
        raise ValueError("AudioFile not mounted")

    if mounted and (not mount_expected):
        raise ValueError("AudioFile mounted")
