"""Base face database"""

import pathlib
import json
import os

import numpy as np


class Person:
    def __init__(self, person_id, base_path):

        self._person_id = person_id
        self._base_path = pathlib.Path(base_path)

        self._params_path = self._base_path / "rps" / f"{person_id:d}"

        # count the number of 'samples' as the number of parameter files
        n_samp = len(os.listdir(self._params_path))


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
