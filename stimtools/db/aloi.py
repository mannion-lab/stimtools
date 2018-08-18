import os
import collections

import numpy as np

import imageio

import skimage.color

import stimtools.utils

try:
    base_path = os.environ["ALOI_PATH"]
except KeyError:
    base_path = os.path.expanduser("~/science/db/aloi")


def get_db_info():

    obj = collections.namedtuple(
        typename="obj",
        field_names=[
            "num",
            "name",
            "material",
            "stained",
            "properties"
        ]
    )

    obj_ann = []

    header_dict = {
        "num": "No.",
        "name": "Object name",
        "material": "Material",
        "stained": "Stained",
        "properties": "Surface properties"
    }

    with open(conf.aloi_ann_path, "r") as ann_file:

        header = ann_file.readline().strip().split("\t")

        info_line = ann_file.readline()

        while len(info_line) > 0:

            info = info_line.strip("\n\r").split("\t")

            assert len(info) == len(header)

            info_dict = {
                h_key: info[header.index(header_dict[h_key])]
                for h_key in header_dict.keys()
            }

            # some cleaning up of the names
            info_dict["name"] = info_dict["name"].replace("\"", "")
            info_dict["name"] = " ".join(info_dict["name"].split())
            info_dict["name"] = info_dict["name"].lower()
            info_dict["name"] = info_dict["name"].replace("\x92", "")
            info_dict["name"] = info_dict["name"].replace("\x85", "")
            info_dict["name"] = info_dict["name"].replace(".", "")

            info_dict["num"] = int(info_dict["num"].strip("."))

            curr_ann = obj(**info_dict)

            obj_ann.append(curr_ann)

            info_line = ann_file.readline()

    return obj_ann


def load_image(
    obj_num,
    illum_num,
    cam_num=1,
    add_mask=False,
    apply_mask=False,
    greyscale=False,
    cielab=False,
    pow2_pad=True
):

    img_fname = "{n:d}_l{l:d}c{c:d}.png".format(
        n=obj_num, l=illum_num, c=cam_num
    )

    img_path = os.path.join(
        base_path,
        "png",
        "{n:d}".format(n=obj_num),
        img_fname
    )

    img = imageio.imread(img_path)

    if greyscale:
        img = skimage.color.rgb2gray(img)

    if cielab:
        img = skimage.color.rgb2lab(img)

    if not greyscale:
        img = img.astype("float") / 255.0

    if add_mask or apply_mask:
        mask = load_mask(conf, obj_num, cam_num)

    if add_mask:

        if greyscale:
            img = img[..., np.newaxis]

        img = np.concatenate((img, mask[..., np.newaxis]), axis=-1)

    if apply_mask:

        if not greyscale:
            mask = mask[..., np.newaxis]

        mask = mask.astype("float") / 255.0

        img *= mask

    if pow2_pad:
        img = stim.utils.pad_image(img)

    return img


def load_mask(
    conf,
    obj_num,
    cam_num=1,
    pow2_pad=True
):

    img_fname = "{n:d}_c{c:d}.png".format(
        n=obj_num, c=cam_num
    )

    img_path = os.path.join(
        base_path,
        "mask",
        "{n:d}".format(n=obj_num),
        img_fname
    )

    img = imageio.imread(img_path)

    if pow2_pad:
        img = stimtools.utils.pad_image(img)

    return img


