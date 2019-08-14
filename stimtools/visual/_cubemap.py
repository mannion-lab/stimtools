import ctypes

import numpy as np

import imageio

import OpenGL.GL as gl


# (row, col) indices of the faces
face_locs = {
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_X: (1, 2),
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_X: (1, 0),
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Y: (0, 1),
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Y: (2, 1),
    gl.GL_TEXTURE_CUBE_MAP_POSITIVE_Z: (1, 1),
    gl.GL_TEXTURE_CUBE_MAP_NEGATIVE_Z: (1, 3),
}

vert_shader = """
#version 330 core

layout (location = 0) in vec3 pos;

out vec3 texcoord;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 rotate;

void main()
{
    texcoord = pos;
    vec4 npos = projection * view * rotate * vec4(pos, 1.0);
    gl_Position = npos.xyww;
}
"""

frag_shader = """
#version 330 core

out vec4 FragColor;

in vec3 texcoord;

uniform samplerCube cubemap;
uniform float alpha;

void main()
{
    FragColor = texture(cubemap, texcoord) * alpha;
}
"""

vertices = np.array(
    [
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        +1.0,
        -1.0,
        +1.0,
        +1.0,
        -1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        +1.0,
        -1.0,
        +1.0,
        +1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        +1.0,
        +1.0,
        -1.0,
        -1.0,
        +1.0,
        -1.0,
        -1.0,
        -1.0,
        -1.0,
        +1.0,
        +1.0,
        -1.0,
        +1.0,
    ]
).astype("float32")

n_vertices = len(vertices) // 3


class CubeMap:
    def __init__(self, cube_map_img, alpha=1.0):

        # load the image
        if not isinstance(cube_map_img, np.ndarray):
            cube_map_img = np.asarray(imageio.imread(cube_map_img))

        (img_h, img_w, _) = cube_map_img.shape
        face_size = img_h // 3
        assert img_w == face_size * 4

        # generate a cubemap texture
        self.i_tex = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.i_tex)

        for (target, (i_row, i_col)) in face_locs.items():

            row_slice = slice(i_row * face_size, i_row * face_size + face_size)
            col_slice = slice(i_col * face_size, i_col * face_size + face_size)

            face = np.copy(cube_map_img[row_slice, col_slice, :])

            # by using sRGB as the internal format, the textures are transformed into
            # linear space internally
            gl.glTexImage2D(
                target,  # target
                0,  # level of detail
                gl.GL_SRGB,  # internal format
                face_size,  # width
                face_size,  # height
                0,  # border
                gl.GL_RGB,  # format
                gl.GL_UNSIGNED_BYTE,  # type
                face,  # data
            )

        for param in ("MIN", "MAG"):
            gl.glTexParameteri(
                gl.GL_TEXTURE_CUBE_MAP,
                getattr(gl, "GL_TEXTURE_" + param + "_FILTER"),
                gl.GL_LINEAR,
            )
        for param in "STR":
            gl.glTexParameteri(
                gl.GL_TEXTURE_CUBE_MAP,
                getattr(gl, "GL_TEXTURE_WRAP_" + param),
                gl.GL_CLAMP_TO_EDGE,
            )

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

        loc = gl.glGetUniformLocation(self.program, "cubemap")
        gl.glUniform1i(loc, 0)

        self.i_alpha = gl.glGetUniformLocation(self.program, "alpha")
        gl.glUniform1i(loc, 0)

        # set up the geometry
        i_pos = gl.glGetAttribLocation(self.program, "pos")
        self.i_vao = gl.glGenVertexArrays(1)
        i_vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.i_vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, i_vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,  # target
            vertices.nbytes,  # size
            vertices,  # data
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

        self.i_proj = gl.glGetUniformLocation(self.program, "projection")
        self.i_view = gl.glGetUniformLocation(self.program, "view")
        self.i_rotate = gl.glGetUniformLocation(self.program, "rotate")

        # set the rotation matrix to null
        self.set_rotate(rotate=np.eye(4).T)

        gl.glUseProgram(0)

        gl.glEnable(gl.GL_TEXTURE_CUBE_MAP_SEAMLESS)

        self.alpha = alpha

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, alpha):
        self._alpha = alpha

        gl.glUseProgram(self.program)
        gl.glUniform1f(self.i_alpha, alpha)
        gl.glUseProgram(0)

    def set_view(self, view):

        view[:, -1] = 0

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

    def set_rotate(self, rotate):

        gl.glUseProgram(self.program)

        gl.glUniformMatrix4fv(
            self.i_rotate,  # location
            1,  # count
            gl.GL_TRUE,  # transpose
            rotate,  # value
        )

        gl.glUseProgram(0)

    def draw(self):
        gl.glUseProgram(self.program)
        gl.glBindVertexArray(self.i_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_CUBE_MAP, self.i_tex)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, n_vertices)
        gl.glBindVertexArray(0)
        gl.glUseProgram(0)
