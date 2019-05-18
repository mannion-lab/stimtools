import os

import numpy as np

import soundfile
import resampy


def load_brir(h_pos, d_pos, angle, db_path=None, head_rotation=0):

    if db_path is None:
        db_path = "/home/damien/science/db/sbs_brir"

    assert os.path.isdir(db_path)

    # potential depth values
    d_lut = {-1.0: "-1", -0.5: "-0pt5", +0.0: "0", +0.5: "0pt5", +1.0: "1"}

    # potential horizontal values
    h_lut = {-1.0: "-1", -0.5: "-0pt5", +0.0: "0"}

    brir_path = os.path.join(
        db_path,
        "SBSBRIR_x{d:s}y{h:s}_LS{r:d}deg.wav".format(
            d=d_lut[d_pos], h=h_lut[h_pos], r=angle
        ),
    )

    (brir, brir_sr) = soundfile.read(brir_path)

    assert brir_sr == 48000

    (_, n_channels) = brir.shape

    # expecting there to be 2 channels for each of the 360 head rotations
    assert n_channels == 720

    i_brir_channel_l = head_rotation * 2
    i_brir_channel_r = i_brir_channel_l + 1
    i_brir_channels = slice(i_brir_channel_l, i_brir_channel_r + 1)

    brir = brir[:, i_brir_channels]

    return brir


def sbs_brir_convolve(
    source_wave, h_pos, d_pos, angle, db_path, wav_path=None, sample_rate=44100
):
    """Convolve a source waveform with the BRIR from the SBS dataset.

    Parameters
    ----------
    source_wave: numpy array (1D)
        Source waveform. This is assumed to be at the BRIR sample rate (48kHz).
    h_pos: float, {-1.0, -0.5, 0.0}
        Horizontal position of the loudspeaker.
    d_pos: float, {-1.0, -0.5, 0.0, 0.5, 1.0}
        Depth position of the loudspeaker.
    angle: int, {0, 30, 45, 90, 110, 135, 180, 225, 250, 270, 315, 330}
        Angular position of the loudspeaker, in degrees.
    db_path: string
        Path to the SBS BRIR database.
    wav_path: string or None, optional
        Path to write the convolved waveform to a WAV file.
    head_rotation: int, (0, 360], optional
        Rotation of the dummy head, in degrees. Note that the recordings were
        in 2 degree increments.
    sample_rate: int, optional
        Sample rate of the convolved waveform.

    """

    brir = load_brir(h_pos, d_pos, angle, db_path)

    brir_sr = 48000

    wave = np.concatenate(
        [np.convolve(source_wave, brir[:, i_lr])[:, np.newaxis] for i_lr in range(2)],
        axis=1,
    )

    # now to resample
    wave = resampy.resample(x=wave, sr_orig=brir_sr, sr_new=sample_rate, axis=0)

    if wav_path is not None:

        if os.path.exists(wav_path):
            os.remove(wav_path)

        soundfile.write(
            file=wav_path,
            data=wave,
            samplerate=sample_rate,
            format="WAV",
            subtype="PCM_16",
        )

    return wave
