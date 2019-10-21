import ctypes

import numpy as np

try:
    import imageio
except ImportError:
    pass

import OpenGL.GL as gl

try:
    import pymesh
except ImportError:
    pass


vert_shader = """
#version 330 core

layout (location = 0) in vec3 pos;
layout (location = 1) in vec3 normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec3 world_pos;
out vec3 nrm;

void main()
{
    // calculate the position in clip space
    gl_Position = projection * view * model * vec4(pos, 1.0);

    // for the lighting, we need the vertices in world space
    world_pos = vec3(model * vec4(pos, 1.0));

    // the lighting also needs the normals, so pass those along
    nrm = normal;
}
"""

frag_shader = """
#version 330 core

uniform vec3 colour;
uniform vec3 lightsource_dir;
uniform float ambient;

in vec3 world_pos;
in vec3 nrm;

out vec4 FragColor;

void main()
{

    // normalise the normal vector
    vec3 nrm_n = normalize(nrm);
    //vec3 light_dir = normalize(vec3(0,1000,0) - world_pos);
    vec3 light_dir = normalize(lightsource_dir - world_pos);

    float diffuse = max(dot(nrm_n, light_dir), 0.0);

    FragColor = vec4((diffuse + ambient) * colour, 1.0);
}
"""

points = np.array(
    [
        -0.52573111,
        +0.85065081,
        +0.00000000,
        -0.85065081,
        +0.00000000,
        +0.52573111,
        +0.00000000,
        +0.52573111,
        +0.85065081,
        -0.52573111,
        +0.85065081,
        +0.00000000,
        +0.00000000,
        +0.52573111,
        +0.85065081,
        +0.52573111,
        +0.85065081,
        +0.00000000,
        -0.52573111,
        +0.85065081,
        +0.00000000,
        +0.52573111,
        +0.85065081,
        +0.00000000,
        +0.00000000,
        +0.52573111,
        -0.85065081,
        -0.52573111,
        +0.85065081,
        +0.00000000,
        +0.00000000,
        +0.52573111,
        -0.85065081,
        -0.85065081,
        +0.00000000,
        -0.52573111,
        -0.52573111,
        +0.85065081,
        +0.00000000,
        -0.85065081,
        +0.00000000,
        -0.52573111,
        -0.85065081,
        +0.00000000,
        +0.52573111,
        +0.52573111,
        +0.85065081,
        +0.00000000,
        +0.00000000,
        +0.52573111,
        +0.85065081,
        +0.85065081,
        +0.00000000,
        +0.52573111,
        +0.00000000,
        +0.52573111,
        +0.85065081,
        -0.85065081,
        +0.00000000,
        +0.52573111,
        +0.00000000,
        -0.52573111,
        +0.85065081,
        -0.85065081,
        +0.00000000,
        +0.52573111,
        -0.85065081,
        +0.00000000,
        -0.52573111,
        -0.52573111,
        -0.85065081,
        +0.00000000,
        -0.85065081,
        +0.00000000,
        -0.52573111,
        +0.00000000,
        +0.52573111,
        -0.85065081,
        +0.00000000,
        -0.52573111,
        -0.85065081,
        +0.00000000,
        +0.52573111,
        -0.85065081,
        +0.52573111,
        +0.85065081,
        +0.00000000,
        +0.85065081,
        +0.00000000,
        -0.52573111,
        +0.52573111,
        -0.85065081,
        +0.00000000,
        +0.85065081,
        +0.00000000,
        +0.52573111,
        +0.00000000,
        -0.52573111,
        +0.85065081,
        +0.52573111,
        -0.85065081,
        +0.00000000,
        +0.00000000,
        -0.52573111,
        +0.85065081,
        -0.52573111,
        -0.85065081,
        +0.00000000,
        +0.52573111,
        -0.85065081,
        +0.00000000,
        -0.52573111,
        -0.85065081,
        +0.00000000,
        +0.00000000,
        -0.52573111,
        -0.85065081,
        +0.52573111,
        -0.85065081,
        +0.00000000,
        +0.00000000,
        -0.52573111,
        -0.85065081,
        +0.85065081,
        +0.00000000,
        -0.52573111,
        +0.52573111,
        -0.85065081,
        +0.00000000,
        +0.85065081,
        +0.00000000,
        -0.52573111,
        +0.85065081,
        +0.00000000,
        +0.52573111,
        +0.00000000,
        +0.52573111,
        +0.85065081,
        +0.00000000,
        -0.52573111,
        +0.85065081,
        +0.85065081,
        +0.00000000,
        +0.52573111,
        -0.52573111,
        -0.85065081,
        +0.00000000,
        +0.00000000,
        -0.52573111,
        +0.85065081,
        -0.85065081,
        +0.00000000,
        +0.52573111,
        +0.00000000,
        -0.52573111,
        -0.85065081,
        -0.52573111,
        -0.85065081,
        +0.00000000,
        -0.85065081,
        +0.00000000,
        -0.52573111,
        +0.85065081,
        +0.00000000,
        -0.52573111,
        +0.00000000,
        -0.52573111,
        -0.85065081,
        +0.00000000,
        +0.52573111,
        -0.85065081,
        +0.85065081,
        +0.00000000,
        +0.52573111,
        +0.85065081,
        +0.00000000,
        -0.52573111,
        +0.52573111,
        +0.85065081,
        +0.00000000,
    ]
).astype("float32")

normals = np.array(
    [
        -0.57735027,
        +0.57735027,
        +0.57735027,
        -0.57735027,
        +0.57735027,
        +0.57735027,
        -0.57735027,
        +0.57735027,
        +0.57735027,
        +0.00000000,
        +0.93417236,
        +0.35682209,
        +0.00000000,
        +0.93417236,
        +0.35682209,
        +0.00000000,
        +0.93417236,
        +0.35682209,
        +0.00000000,
        +0.93417236,
        -0.35682209,
        +0.00000000,
        +0.93417236,
        -0.35682209,
        +0.00000000,
        +0.93417236,
        -0.35682209,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        -0.93417236,
        +0.35682209,
        +0.00000000,
        -0.93417236,
        +0.35682209,
        +0.00000000,
        -0.93417236,
        +0.35682209,
        +0.00000000,
        +0.57735027,
        +0.57735027,
        +0.57735027,
        +0.57735027,
        +0.57735027,
        +0.57735027,
        +0.57735027,
        +0.57735027,
        +0.57735027,
        -0.35682209,
        +0.00000000,
        +0.93417236,
        -0.35682209,
        +0.00000000,
        +0.93417236,
        -0.35682209,
        +0.00000000,
        +0.93417236,
        -0.93417236,
        -0.35682209,
        +0.00000000,
        -0.93417236,
        -0.35682209,
        +0.00000000,
        -0.93417236,
        -0.35682209,
        +0.00000000,
        -0.35682209,
        +0.00000000,
        -0.93417236,
        -0.35682209,
        +0.00000000,
        -0.93417236,
        -0.35682209,
        +0.00000000,
        -0.93417236,
        +0.57735027,
        +0.57735027,
        -0.57735027,
        +0.57735027,
        +0.57735027,
        -0.57735027,
        +0.57735027,
        +0.57735027,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        +0.57735027,
        +0.57735027,
        -0.57735027,
        +0.57735027,
        +0.57735027,
        -0.57735027,
        +0.57735027,
        +0.00000000,
        -0.93417236,
        +0.35682209,
        +0.00000000,
        -0.93417236,
        +0.35682209,
        +0.00000000,
        -0.93417236,
        +0.35682209,
        +0.00000000,
        -0.93417236,
        -0.35682209,
        +0.00000000,
        -0.93417236,
        -0.35682209,
        +0.00000000,
        -0.93417236,
        -0.35682209,
        +0.57735027,
        -0.57735027,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        -0.57735027,
        +0.93417236,
        -0.35682209,
        +0.00000000,
        +0.93417236,
        -0.35682209,
        +0.00000000,
        +0.93417236,
        -0.35682209,
        +0.00000000,
        +0.35682209,
        +0.00000000,
        +0.93417236,
        +0.35682209,
        +0.00000000,
        +0.93417236,
        +0.35682209,
        +0.00000000,
        +0.93417236,
        -0.57735027,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        -0.57735027,
        +0.57735027,
        -0.57735027,
        -0.57735027,
        -0.57735027,
        -0.57735027,
        -0.57735027,
        -0.57735027,
        -0.57735027,
        -0.57735027,
        -0.57735027,
        +0.35682209,
        +0.00000000,
        -0.93417236,
        +0.35682209,
        +0.00000000,
        -0.93417236,
        +0.35682209,
        +0.00000000,
        -0.93417236,
        +0.93417236,
        +0.35682209,
        +0.00000000,
        +0.93417236,
        +0.35682209,
        +0.00000000,
        +0.93417236,
        +0.35682209,
        +0.00000000,
    ]
).astype("float32")

n_vertices = len(points) // 3

vertex_data = np.concatenate((points, normals)).astype("float32")


class Sphere:
    def __init__(self):

        # set up the shader
        i_vert = gl.glCreateShader(gl.GL_VERTEX_SHADER)
        gl.glShaderSource(i_vert, vert_shader)
        i_frag = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
        gl.glShaderSource(i_frag, frag_shader)

        self.program = gl.glCreateProgram()
        gl.glAttachShader(self.program, i_vert)
        gl.glAttachShader(self.program, i_frag)
        gl.glCompileShader(i_vert)
        gl.glCompileShader(i_frag)

        gl.glLinkProgram(self.program)
        gl.glValidateProgram(self.program)

        gl.glUseProgram(self.program)

        # set up the geometry
        i_pos = gl.glGetAttribLocation(self.program, "pos")
        i_normal = gl.glGetAttribLocation(self.program, "normal")

        self.i_vao = gl.glGenVertexArrays(1)
        i_vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.i_vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, i_vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,  # target
            vertex_data.nbytes,  # size
            vertex_data,  # data
            gl.GL_STATIC_DRAW,  # usage
        )

        gl.glEnableVertexAttribArray(i_pos)
        gl.glVertexAttribPointer(
            i_pos,  # index
            3,  # size
            gl.GL_FLOAT,  # type
            gl.GL_FALSE,  # normalisation
            0,  # stride
            ctypes.c_void_p(0),  # pointer
        )

        gl.glEnableVertexAttribArray(i_normal)
        gl.glVertexAttribPointer(
            i_normal,  # index
            3,  # size
            gl.GL_FLOAT,  # type
            gl.GL_FALSE,  # normalisation
            0,  # stride
            ctypes.c_void_p(len(points) * 4),  # pointer
        )

        self.i_proj = gl.glGetUniformLocation(self.program, "projection")
        self.i_view = gl.glGetUniformLocation(self.program, "view")
        self.i_model = gl.glGetUniformLocation(self.program, "model")
        self.i_colour = gl.glGetUniformLocation(self.program, "colour")
        self.i_lightsource_dir = gl.glGetUniformLocation(
            self.program, "lightsource_dir"
        )
        self.i_ambient = gl.glGetUniformLocation(self.program, "ambient")

        # set the rotation matrix to null
        self.set_model(model=np.eye(4).T)
        gl.glUseProgram(0)

    def draw(self):
        gl.glUseProgram(self.program)

        gl.glBindVertexArray(self.i_vao)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, n_vertices)
        gl.glBindVertexArray(0)
        gl.glUseProgram(0)

    def set_view(self, view):

        gl.glUseProgram(self.program)

        gl.glUniformMatrix4fv(
            self.i_view, 1, gl.GL_TRUE, view  # location  # count  # transpose  # value
        )

        gl.glUseProgram(0)

    def set_proj(self, proj):

        gl.glUseProgram(self.program)

        gl.glUniformMatrix4fv(
            self.i_proj, 1, gl.GL_TRUE, proj  # location  # count  # transpose  # value
        )

        gl.glUseProgram(0)

    def set_model(self, model):

        gl.glUseProgram(self.program)

        gl.glUniformMatrix4fv(
            self.i_model,  # location
            1,  # count
            gl.GL_TRUE,  # transpose
            model,  # value
        )

        gl.glUseProgram(0)

    def set_colour(self, colour):

        gl.glUseProgram(self.program)

        gl.glUniform3fv(self.i_colour, 1, colour)  # location  # count  # value

        gl.glUseProgram(0)

    def set_lightsource_dir(self, lightsource_dir):

        gl.glUseProgram(self.program)

        gl.glUniform3fv(
            self.i_lightsource_dir, 1, lightsource_dir  # location  # count  # value
        )

        gl.glUseProgram(0)

    def set_ambient(self, ambient):

        gl.glUseProgram(self.program)

        gl.glUniform1fv(self.i_ambient, 1, ambient)  # location  # value

        gl.glUseProgram(0)


def gen_geometry(print_code=True):

    sphere = pymesh.generate_icosphere(radius=1.0, center=[0, 0, 0])

    n_vertices = sphere.num_faces * 3

    vertices = np.full((n_vertices, 3), np.nan)

    for i_face in range(sphere.num_faces):

        face_vert = sphere.vertices[sphere.faces[i_face, :], :]

        i_vert = range(i_face * 3, i_face * 3 + 3)

        assert np.all(np.isnan(vertices[i_vert, :]))

        vertices[i_vert, :] = face_vert

    faces = np.arange(n_vertices).reshape((sphere.num_faces, 3))

    mesh = pymesh.form_mesh(vertices=vertices, faces=faces)

    mesh.add_attribute("vertex_normal")
    normals = mesh.get_attribute("vertex_normal")

    if print_code:
        to_print = "points = np.array(\n    [\n"
        for point in vertices.flat:
            to_print += " " * 4 * 2 + f"{point:+.08f},\n"
        to_print += " " * 4 + ']\n).astype("float32")\n'
        to_print += "\n"

        to_print += "normals = np.array(\n    [\n"
        for point in normals.flat:
            to_print += " " * 4 * 2 + f"{point:+.08f},\n"
        to_print += " " * 4 + ']\n).astype("float32")\n'
        to_print += "\n"

        print(to_print)

    return (vertices, normals, mesh)
