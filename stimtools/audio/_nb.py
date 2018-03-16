import os
import tempfile

import IPython.display as ipd

import soundfile


def nb_player(sound, sr, vol_reduce=0.1):

    # have to write an intermediate file because otherwise it automatically
    # normalises :(
    temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

    temp.close()

    soundfile.write(temp.name, sound * vol_reduce, samplerate=sr)

    display_obj = ipd.display(ipd.Audio(temp.name, rate=sr))

    os.remove(temp.name)

    return display_obj
