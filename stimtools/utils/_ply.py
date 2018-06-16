
import numpy as np

try:
    import plyfile
except ImportError:
    pass


def create_ply(
    vertices,
    faces,
    save_path=None,
    text=True,
    replace_endings=False
):

    vertex_dtype = [(dim, "f4") for dim in "xyz"]
    vertex_array = np.array(vertices, dtype=vertex_dtype)
    vertex_el = plyfile.PlyElement.describe(vertex_array, "vertex")

    face_dtype = [("vertex_indices", "i4", (4, ))]
    face_array = np.array(faces, dtype=face_dtype)
    face_el = plyfile.PlyElement.describe(face_array, "face")

    data = plyfile.PlyData([vertex_el, face_el], text=text)

    if save_path is not None:
        data.write(save_path)

        if replace_endings:

            with open(save_path, "rb") as handle:
                data_str = handle.read()

            data_str = data_str.replace(
                "\r".encode("u8"),
                "".encode("u8")
            )

            with open(save_path, "wb") as handle:
                handle.write(data_str)

    return data
