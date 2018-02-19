
import numpy as np

try:
    import plyfile
except ImportError:
    pass


def create_ply(vertices, faces, save_path=None):

    vertex_dtype = [(dim, "f4") for dim in "xyz"]
    vertex_array = np.array(vertices, dtype=vertex_dtype)
    vertex_el = plyfile.PlyElement.describe(vertex_array, "vertex")

    face_dtype = [("vertex_indices", "i4", (4, ))]
    face_array = np.array(faces, dtype=face_dtype)
    face_el = plyfile.PlyElement.describe(face_array, "face")

    data = plyfile.PlyData([vertex_el, face_el], text=True)

    if save_path is not None:
        data.write(save_path)

    return data
