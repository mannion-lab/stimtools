import ctypes

import numpy as np

import imageio

import OpenGL.GL as gl


vert_shader = """
#version 330 core

layout (location = 0) in vec3 pos;

out vec3 texcoord;

void main()
{
    texcoord = pos;
    vec4 npos = projection * view * vec4(pos, 1.0);
    gl_Position = npos.xyww;
}
"""

frag_shader = """
#version 330 core

out vec4 FragColor;

in vec3 texcoord;

uniform sampler2D img;

void main()
{
    FragColor = texture(img, texcoord);
}
"""

points = np.array(
    [
        -1.0, -1.0, 0.0,
        +1.0, -1.0, 0.0,
        -1.0, +1.0, 0.0,
        -1.0, +1.0, 0.0,
        +1.0, -1.0, 0.0,
        +1.0, +1.0, 0.0,
    ]
).astype("float32")

n_vertices = len(points) // 3


class ImageStim:
    def __init__(self, img, srgb=True):

        # load the image
        if not isinstance(img, np.ndarray):
            img = np.asarray(imageio.imread(img))

        (img_h, img_w, img_c) = img.shape

        if img_c == 3:
            # add an alpha channel, if it doesn't have one
            alpha = np.ones_like(img[..., (0, )])
            img = np.concatenate((img, alpha), axis=-1)

        if srgb:
            fmt = "GL_SRGB_ALPHA"
        else:
            fmt = "GL_RGBA"

        self.i_tex = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.i_tex)

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,  # target
            0, # level of detail
            getattr(gl, fmt),
            img_w,  # width
            img_h, # height
            0,  # border
            GL_RGBA,  # format
            gl.GL_UNSIGNED_BYTE, # type
            img,
        )

        for param in "ST":
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

        # set up the geometry
        i_pos = gl.glGetAttribLocation(self.program, "pos")
        self.i_vao = gl.glGenVertexArrays(1)
        i_vbo = gl.glGenBuffers(1)

        gl.glBindVertexArray(self.i_vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, i_vbo)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,  # target
            points.nbytes,  # size
            points,  # data
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

        gl.glUseProgram(0)

    def draw(self):
        gl.glUseProgram(self.program)
        gl.glBindVertexArray(self.i_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.i_tex)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, n_vertices)
        gl.glBindVertexArray(0)
        gl.glUseProgram(0)
