import soundfile


def save(wav_path, waveform, sr, wav_type="PCM_16"):

    soundfile.write(
        file=wav_path, data=waveform, samplerate=sr, format="WAV", subtype=wav_type
    )
