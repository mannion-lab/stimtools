import os

import soundfile

try:
    import librosa
except ImportError:
    pass

try:
    base_path = os.environ["TRAER_IR_PATH"]
except KeyError:
    base_path = os.path.expanduser("~/science/db/natural_ir")


def get_db_info():

    filenames = [
        filename
        for filename in os.listdir(base_path)
        if filename.endswith("wav")
    ]

    filenames = sorted(filenames)

    return filenames


def load_ir(ir_filename, new_sr=None):

    ir_path = os.path.join(base_path, ir_filename)

    if new_sr is None:
        (ir, ir_sr) = soundfile.read(file=ir_path)
    else:
        (ir, ir_sr) = librosa.load(
            path=ir_path,
            sr=new_sr
        )

    return (ir, ir_sr)
