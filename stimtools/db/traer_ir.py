import os

import soundfile

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


def load_ir(ir_filename):

    ir_path = os.path.join(base_path, ir_filename)

    (ir, ir_sr) = soundfile.read(file=ir_path)

    return (ir, ir_sr)
