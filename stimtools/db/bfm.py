"""Basel face model"""


import pathlib
import os

import numpy as np
import scipy.io

try:
    import trimesh
except ImportError:
    pass

try:
    import pyrender
except ImportError:
    pass


class Person:
    def __init__(self, model=None):
        """An instance from the Basel Face Model (2009).

        Parameters
        ----------
        model: output from scipy.io.loadmat, or str, or None
            Either the BFM model (01_MorphableModel.mat), a string containing its path,
            or None - in which case it will try and find it in the default location.

        """

        # try to auto find path model if not explicitly provided
        if model is None:
            try:
                model = os.environ["BFM_MODEL_PATH"]
            except KeyError:
                base_path = pathlib.Path("~/science/db/basel_face_model/PublicMM1/")
                model = str(base_path.expanduser() / "01_MorphableModel.mat")

        if isinstance(model, str):
            model = scipy.io.loadmat(
                file_name=model, struct_as_record=False, squeeze_me=True
            )

        self._model = model

        # triangle list
        self._tl = self._model["tl"]

        self.dims = {
            dim_name: {
                param.lower(): model[f"{dim_name:s}{param:s}"]
                for param in ["MU", "PC", "EV"]
            }
            for dim_name in ["shape", "tex"]
        }

        self._n_vertices = len(self.dims["shape"]["mu"]) // 3

        for dim in self.dims:
            self.set_dim(dim=dim, coefs=np.zeros(1))

    def set_dim(self, dim, coefs):
        """Set the head configuration from model coefficients.

        Parameters
        ----------
        dim: string, {"shape", "tex"}
            Which dimension the coefficents are for.
        coefs: array of floats
            Principal component coefficients. Can be fewer than those in the model.

        Notes
        -----
        This sets the `vals` item in the relevant `dims` dict, overwriting if it is
        already there.

        """

        assert dim in self.dims

        n_coef = len(coefs)

        (mu, pc, ev) = [self.dims[dim][param] for param in ["mu", "pc", "ev"]]

        vals = mu + pc[:, :n_coef] @ (coefs * ev[:n_coef])

        vals = np.reshape(vals, (len(vals) // 3, 3))

        self.dims[dim]["vals"] = vals

    def render(self):

        vertices = self.dims["shape"]["vals"]
        vertices /= np.max(np.abs(vertices))

        vertices[:, -1] -= 100

        faces = self._tl - 1
        colours = self.dims["tex"]["vals"]

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=colours)

        mesh.invert()

        self._mesh = mesh

        camera = pyrender.OrthographicCamera(xmag=1.0, ymag=1.0)

        #material = pyrender.MetallicRoughnessMaterial(doubleSided=True)

        obj = pyrender.Mesh.from_trimesh(mesh=mesh) #, material=material)

        scene = pyrender.Scene(ambient_light=[1.0] * 3)

        scene.add(camera)
        scene.add(obj)

        self._renderer = pyrender.OffscreenRenderer(
            viewport_width=512, viewport_height=512
        )

        self._scene = scene

        color, depth = self._renderer.render(scene)

        return (color, depth)
