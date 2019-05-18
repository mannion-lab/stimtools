import os

import soundfile

try:
    import librosa
except ImportError:
    pass

try:
    base_path = os.environ["ACE_CORPUS_PATH"]
except KeyError:
    base_path = os.path.expanduser("~/science/db/ACE_corpus/Speech")


def get_db_info():

    db = {}

    filenames = [
        filename for filename in os.listdir(base_path) if filename.endswith("wav")
    ]

    for filename in filenames:

        words_path = filename.replace("wav", "txt")

        with open(os.path.join(base_path, words_path), "r") as words_file:
            words = words_file.read()

        speaker_id = filename[:2]

        if words not in db:
            db[words] = {speaker_id: filename}
        else:
            db[words][speaker_id] = filename

    return db


def load(filename, new_sr=None):

    filename = os.path.join(base_path, filename)

    if new_sr is None:
        (w, sr) = soundfile.read(file=filename)
    else:
        (w, sr) = librosa.load(path=filename, sr=new_sr)

    return (w, sr)
