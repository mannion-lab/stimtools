"""Basel face model"""


import pathlib
import os

import numpy as np
import scipy.io
import scipy.spatial.transform

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

    def set_dim(self, dim, coefs, clip_warn=False):
        """Set the head configuration from model coefficients.

        Parameters
        ----------
        dim: string, {"shape", "tex"}
            Which dimension the coefficents are for.
        coefs: array of floats
            Principal component coefficients. Can be fewer than those in the model.
        clip_warn: bool
            Whether to warn when `tex` parameters cause the values to be outside of the
            [0, 255] interval.

        Notes
        -----
        This sets the `vals` item in the relevant `dims` dict, overwriting if it is
        already there.

        """

        assert dim in self.dims

        n_coef = len(coefs)

        (mu, pc, ev) = [self.dims[dim][param] for param in ["mu", "pc", "ev"]]

        vals = mu + pc[:, :n_coef] @ (coefs * ev[:n_coef])

        if dim == "tex":
            if np.any(np.logical_or(vals < 0, vals > 255)):
                if clip_warn:
                    print("Clipping")
                vals = np.clip(vals, 0, 255)

        vals = np.reshape(vals, (len(vals) // 3, 3))

        self.dims[dim]["vals"] = vals

    def export_ply(self, ply_path):

        vertices = self.dims["shape"]["vals"]

        # this brings them into about the [-15, +15] range
        vertices /= 10_000

        faces = self._tl - 1

        colours = self.dims["tex"]["vals"]

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=colours)

        mesh.invert()

        mesh.export(file_obj=ply_path)

    def render(self, pose_deg=25.0, light_pose_deg=-25.0, gamma=1.0):

        vertices = self.dims["shape"]["vals"]
        vertices /= np.max(np.abs(vertices))

        faces = self._tl - 1

        # these are linear (I think) but the renderer needs them in sRGB
        colours = self.dims["tex"]["vals"]

        srgb_colours = colours / 255.0

        srgb_colours = np.where(
            srgb_colours < 0.0031308,
            srgb_colours * 12.92,
            1.055 * (srgb_colours ** (1.0 / 2.4)) - 0.055,
        )

        srgb_colours *= 255.0

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, vertex_colors=colours)

        mesh.invert()

        self._mesh = mesh

        camera = pyrender.OrthographicCamera(xmag=1.0, ymag=1.0)

        pose_vec = scipy.spatial.transform.Rotation.from_rotvec(
            [0, np.radians(pose_deg), 0]
        )

        pose_mat = np.eye(4)
        pose_mat[:3, :3] = pose_vec.as_dcm()
        pose_mat[2, -1] = -100

        material = pyrender.material.SpecularGlossinessMaterial(
            diffuseFactor=1.0, glossinessFactor=0.0
        )

        obj = pyrender.Mesh.from_trimesh(
            mesh=mesh, poses=pose_mat[np.newaxis, ...]  # material=material
        )

        self._obj = obj

        light = pyrender.DirectionalLight(intensity=5.0)

        light_pose_vec = scipy.spatial.transform.Rotation.from_rotvec(
            [0, np.radians(light_pose_deg), 0]
        )
        light_pose_mat = np.eye(4)
        light_pose_mat[:3, :3] = light_pose_vec.as_dcm()

        scene = pyrender.Scene(ambient_light=[0.1] * 3, bg_color=[0] * 4)

        scene.add(camera)
        scene.add(obj)
        scene.add(light, pose=light_pose_mat)

        self._renderer = pyrender.OffscreenRenderer(
            viewport_width=512, viewport_height=512
        )

        self._scene = scene

        flags = (
            pyrender.constants.RenderFlags.NONE
            | pyrender.constants.RenderFlags.RGBA
            | pyrender.constants.RenderFlags.SHADOWS_ALL
        )

        (img, _) = self._renderer.render(scene, flags=flags)

        img = (img / 255.0) ** (1.0 / gamma)
        img = np.round(img * 255.0).astype("uint8")

        return img
