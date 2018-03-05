import os
import collections

import soundfile

import imageio

import skimage.transform

try:
    import panorama_image_cropper
except ImportError:
    pano_avail = False
else:
    pano_avail = True


try:
    base_path = os.environ["ECHO_THIEF_PATH"]
except KeyError:
    base_path = os.path.expanduser("~/science/db/echo_thief")

base_audio_path = os.path.join(base_path, "EchoThiefImpulseResponseLibrary")
base_img_path = os.path.join(base_path, "locations")

name_to_img_lut = {
    "ExerciseAndNutritionSciences": "ExerciseAndNutritionalSciences.JPG",
    "HaleHolisticYogaStudio": "HaleHolisticYogaStudio.JPG .JPG",
    "IslaMujeresCave": "IslaMujeresCave.jpg",
    "PacificHall": "PacificHall.jpg",
    "RacquetballCourt": "RacquetballCourt#4.JPG",
    "WaterplacePark": "WaterPlacePark.JPG",
    "StanleyParkDriveUnderpass": "StanleyParkDrUnderpass.JPG",
    "Commerical&5Underpass": "Commercial_5Underpass.JPG",
    "NaturalSciences": "NaturalSciencesBuilding.jpg",
    "BiomedicalSciences": "BiomedicalBuilding.jpg",
    "3000CStreetGarageStairwell": "CStreetGarageStairwell.JPG",
    "FortalezaDeSanCarlosDeLaCabana ": "FortalezaDeSanCarlosDeLaCabana.JPG",
}

# those without proper panoramas
bad_locs = [
    "BatteryQuarles",
    "StorageTankNo7",
    "TunnelToHeaven",
    "TunnelToHell"
]


def get_db_info():

    locations = {}

    for (dir_path, _, files) in os.walk(base_audio_path):

        category = os.path.basename(dir_path)

        for curr_file in files:

            (file_name, file_ext) = os.path.splitext(curr_file)

            if file_ext != ".wav" or file_name in bad_locs:
                continue

            jpg_name = file_name

            jpg_path = os.path.join(base_img_path, jpg_name + ".JPG")

            if not os.path.exists(jpg_path):
                jpg_path = jpg_path.replace(".JPG", ".JPG .JPG")

            if not os.path.exists(jpg_path):
                jpg_path = jpg_path.replace(".JPG .JPG", ".jpg")

            if not os.path.exists(jpg_path):
                try:
                    jpg_path = os.path.join(
                        base_img_path,
                        name_to_img_lut[file_name]
                    )
                except KeyError:
                    continue

            assert file_name not in locations

            locations[file_name] = {
                "category": category,
                "wav_name": file_name,
                "wav_path": os.path.join(dir_path, curr_file),
                "jpg_path": jpg_path
            }

    # do some checks
    unique_images = [
        loc_info["jpg_path"]
        for loc_info in locations.values()
    ]

    # no image is assigned to two different locations
    assert len(unique_images) == len(set(unique_images))

    if len(locations) == 0:
        raise ValueError(
            """
Database not found at {d:s}.

Try setting the ECHO_THIEF_PATH shell environment variable.
            """.format(d=base_path)
        )

    # sort by key
    locations = collections.OrderedDict(
        sorted(locations.items(), key=lambda x: x[0])
    )

    return locations


def load_ir(loc_name, db_info=None):

    if db_info is None:
        db_info = get_db_info()

    (ir, ir_sr) = soundfile.read(file=db_info[loc_name]["wav_path"])

    return (ir, ir_sr)


def load_img(loc_name, res, fov, theta, db_info=None, resize=True):

    if db_info is None:
        db_info = get_db_info()

    if not pano_avail:

        msg = """
The panorama image extractor is not available.

Run:
    git clone https://github.com/daerduoCarey/PanoramaImageViewer

and then add it to the python path
        """

        raise ImportError(msg)

    img = imageio.imread(db_info[loc_name]["jpg_path"])

    if resize:
        new_dim = (2048, 4096)

        img = skimage.transform.resize(
            img,
            new_dim,
            order=3,
            mode="reflect",
            preserve_range=True
        ).astype("uint8")

    # convert into a roughly non-panoramic image
    img = panorama_image_cropper.crop_panorama_image(
        img, res_x=res[0], res_y=res[1], fov=fov, theta=theta
    )

    return img
