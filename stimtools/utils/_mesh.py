def pymesh_to_povray(mesh, smooth=True, save_path=None):
    """Converts a `pymesh` mesh to POVray format.

    Parameters
    ----------
    mesh: `pymesh.Mesh` object
        Mesh to export.
    smooth: bool, optional
        Whether to interpolate over the faces.
    save_path: str-like, optional
        If provided, save the POVray code to this file.

    Returns
    -------
    pov: str
        POVray `mesh` definition.

    """

    pov = "mesh {\n"

    if smooth:

        if not mesh.has_attribute("vertex_normal"):
            mesh.add_attribute("vertex_normal")

        normals = mesh.get_attribute("vertex_normal")

        normals = normals.reshape((mesh.num_vertices, 3))

    for i_face in range(mesh.num_faces):

        if smooth:
            pov += "\tsmooth_triangle {\n"
        else:
            pov += "\ttriangle {\n"

        rows = []

        for i_vertex in mesh.faces[i_face, :]:

            vertex = mesh.vertices[i_vertex, :]

            xyz = ",".join([f"{vert:.16f}" for vert in vertex])

            row = f"\t\t<{xyz:s}>"

            if smooth:
                normal = normals[i_vertex, :]

                normal_xyz = ",".join([f"{norm:.16f}" for norm in normal])

                row += f"<{normal_xyz:s}>"

            rows.append(row)

        pov += ",".join(rows) + "\n"

        pov += "\t}\n"

    pov += "}"

    if save_path is not None:
        with open(save_path, "w") as save_file:
            save_file.write(pov)

    return pov


def pymesh_to_povray_mesh2(mesh, smooth=True, save_path=None):
    """Converts a `pymesh` mesh to POVray 'mesh2' format.

    Parameters
    ----------
    mesh: `pymesh.Mesh` object
        Mesh to export.
    smooth: bool, optional
        Whether to interpolate over the faces.
    save_path: str-like, optional
        If provided, save the POVray code to this file.

    Returns
    -------
    pov: str
        POVray `mesh` definition.

    """

    pov = "mesh2 {\n"

    (n_vertices, _) = mesh.vertices.shape

    pov += f"vertex_vectors {{ {n_vertices:d}"

    for vertex in mesh.vertices:
        pov += ","
        pov += "<" + ",".join([f"{dim_vertex:.12f}" for dim_vertex in vertex]) + ">"

    pov += "\n}\n"

    if smooth:

        if not mesh.has_attribute("vertex_normal"):
            mesh.add_attribute("vertex_normal")

        normals = mesh.get_attribute("vertex_normal")

        normals = normals.reshape((mesh.num_vertices, 3))

        pov += f"normal_vectors {{ {n_vertices:d}"

        for normal in normals:
            pov += ","
            pov += "<" + ",".join([f"{dim_normal:.12f}" for dim_normal in normal]) + ">"

        pov += "\n}\n"

    (n_faces, _) = mesh.faces.shape

    pov += f"face_indices {{ {n_faces:d}"

    for face in mesh.faces:
        pov += ","
        pov += "<" + ",".join([f"{dim_i:d}" for dim_i in face]) + ">"

    pov += "\n}\n"

    pov += "}"

    if save_path is not None:
        with open(save_path, "w") as save_file:
            save_file.write(pov)

    return pov
