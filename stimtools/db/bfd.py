"""Base face database"""

import pathlib
import json
import os
import pprint

import numpy as np
import scipy.spatial

import imageio


class Population:
    def __init__(self, base_path):

        self._base_path = pathlib.Path(base_path)

        self.people_ids = sorted(
            [int(person_id) for person_id in os.listdir(self._base_path / "img")]
        )
        self.n_people = len(self.people_ids)

        self.people = {
            person_id: Person(person_id=person_id, base_path=base_path)
            for person_id in self.people_ids
        }

    def __repr__(self):
        return pprint.pformat(
            {
                key: value
                for (key, value) in vars(self).items()
                if not key.startswith("_")
            },
            depth=1,
        )

    def calc_similarity(self):

        sim = np.full((self.n_people, self.n_people, 3), np.nan)

        coefs = np.array(
            [
                [getattr(person, f"{att:s}_coefs") for att in ("shape", "reflectance")]
                for person in self.people.values()
            ]
        )

        dist = scipy.spatial.distance.euclidean

        for (i_row, row_id) in enumerate(self.people_ids):
            for (i_col, col_id) in enumerate(self.people_ids):

                if i_row >= i_col:
                    continue

                sim[i_row, i_col, 0] = dist(coefs[i_row, 0, :], coefs[i_col, 0, :])
                sim[i_row, i_col, 1] = dist(coefs[i_row, 1, :], coefs[i_col, 1, :])
                sim[i_row, i_col, 2] = dist(
                    coefs[i_row, ...].flat, coefs[i_col, ...].flat
                )

        self.coefs = coefs
        self.sim = sim

class Person:
    def __init__(self, person_id, base_path):

        self.person_id = person_id
        self._base_path = pathlib.Path(base_path)

        self._params_path = self._base_path / "rps" / f"{person_id:d}"

        # count the number of 'samples' as the number of parameter files
        n_samp = len(os.listdir(self._params_path))

        self.pose_yaws = np.full(n_samp, np.nan)
        self.illum_azimuths = np.full(n_samp, np.nan)

        # store the parameters
        for (i_samp, samp_num) in enumerate(range(1, n_samp + 1)):

            samp_param_path = self._params_path / f"{person_id:d}_{samp_num:d}.rps"

            samp_params = parse_params(param_path=samp_param_path)

            # these are assumed to be the same across samples
            for attr_name in ("shape_coefs", "reflectance_coefs", "image_size_xy"):

                try:
                    assert np.all(getattr(self, attr_name) == samp_params[attr_name])
                except AttributeError:
                    setattr(self, attr_name, samp_params[attr_name])

            self.pose_yaws[i_samp] = samp_params["pose"]["yaw"]
            self.illum_azimuths[i_samp] = samp_params["illum"]["azimuth"]

        self.unique_pose_yaws = np.unique(self.pose_yaws)
        self.unique_illum_azimuths = np.unique(self.illum_azimuths)

    def __repr__(self):
        return pprint.pformat(
            {
                key: value
                for (key, value) in vars(self).items()
                if not key.startswith("_")
            }
        )

    def load_image(self, illum_azimuth=0.0, pose_yaw=0.0, image_type="render"):

        if image_type == "render":
            image_type = ""
        elif image_type in ["albedo", "depth", "illumination", "normals"]:
            image_type = "_" + image_type
        else:
            raise ValueError("Unknown image type")

        samp_match = np.logical_and(
            self.pose_yaws == pose_yaw, self.illum_azimuths == illum_azimuth
        )

        n_match = np.sum(samp_match)

        if n_match == 1:
            i_samp = int(np.flatnonzero(samp_match))
        elif n_match == 0:
            raise ValueError("No samples matching requirements")
        else:
            raise ValueError("Multiple samples matching requirements")

        samp_num = i_samp + 1

        images_path = self._base_path / "img" / f"{self.person_id:d}"
        image_path = images_path / f"{self.person_id:d}_{samp_num:d}{image_type:s}.png"

        image = imageio.imread(uri=image_path)

        return image


def parse_params(param_path):

    with open(param_path, "r") as handle:
        raw_params = json.load(handle)

    params = {
        "shape_coefs": np.array(raw_params["momo"]["shape"]),
        "reflectance_coefs": np.array(raw_params["momo"]["color"]),
        "image_size_xy": np.array(
            [raw_params["imageSize"][dim] for dim in ["width", "height"]]
        ),
        "pose": {
            att: np.round(np.degrees(raw_params["pose"][att]), decimals=12)
            for att in ["roll", "pitch", "yaw"]
        },
    }

    # want to convert the illumination coefficients back to their directions

    illum_coefs = np.array(raw_params["environmentMap"]["coefficients"])

    # the columns are just copies
    assert np.all(illum_coefs[:, (0,)] == illum_coefs)

    illum_coefs = illum_coefs[:, 0]

    # these are from './scala/scalismo/faces/parameters/Illumination.scala'
    n0 = np.sqrt(1.0 / np.pi) / 2.0
    n1 = np.sqrt(3.0 / np.pi) / 2.0
    kappa = np.pi / 1.5

    # these coefficients are:
    # 1 / n0 / pi * ambient
    # y / n1 / kappa * diffuse
    # z / n1 / kappa * diffuse
    # x / n1 / kappa * diffuse

    # first, check that we can get back the ambient (0.5)
    ambient = illum_coefs[0] * np.pi * n0
    np.testing.assert_allclose(ambient, 0.5, rtol=1e-4)

    # now get back the other components
    diffuse = 0.5
    (y, z, x) = (illum_coefs[1:] * kappa * diffuse) / n1

    # right, now what are they?
    # x: r * cos(phi) * sin(theta)
    # y: r * sin(phi) * sin(theta)
    # z: r * cos(theta)

    r = np.sqrt(np.sum(np.array([x, y, z]) ** 2))
    inc = np.degrees(np.arccos(z / r))
    az = np.degrees(np.arctan2(y, x)) - 90.0

    params["illum"] = {
        att: np.round(att_val, decimals=12)
        for (att, att_val) in (("r", r), ("inclination", inc), ("azimuth", az))
    }

    return params
