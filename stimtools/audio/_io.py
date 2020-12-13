import soundfile


def save(wav_path, waveform, sr, wav_format="WAV", wav_type="PCM_16"):

    soundfile.write(
        file=wav_path, data=waveform, samplerate=sr, format=wav_format, subtype=wav_type
    )


def load(wav_path, with_sr=False, *_, **kwargs):

    (wav, sr) = soundfile.read(file=wav_path, **kwargs)

    if with_sr:
        return (wav, sr)
    else:
        return wav
