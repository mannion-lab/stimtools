import ctypes

import numpy as np

try:
    import imageio
except ImportError:
    pass

import OpenGL.GL as gl


vert_shader = """
#version 330 core

layout (location = 0) in vec2 pos;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;
uniform vec2 phase;

out vec2 uv;

void main()
{
    uv = (pos + 1.0) / 2.0 + phase;
    gl_Position = projection * view * model * vec4(pos, 0.0, 1.0);
}
"""

frag_shader = """
#version 330 core

out vec4 FragColor;

in vec2 uv;

uniform float global_alpha;
uniform bool apply_global_alpha;

uniform sampler2D img;

void main()
{
    FragColor = texture(img, uv);

    if (apply_global_alpha) {
        FragColor = vec4(FragColor.rgb, FragColor.a * global_alpha);
    }
}
"""

# just the xy
points = np.array(
    [-1.0, -1.0, +1.0, -1.0, -1.0, +1.0, -1.0, +1.0, +1.0, -1.0, +1.0, +1.0]
).astype("float32")

n_vertices = len(points) // 2


class WorldImageStim:
    def __init__(
        self,
        img,
        proj_mat,
        global_alpha=1.0,
        apply_global_alpha=False,
        srgb=True,
        model=None,
    ):

        self._proj_mat = proj_mat

        self.i_tex = gl.glGenTextures(1)

        self.set_img(img=img, srgb=srgb)

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

        self.i_global_alpha = gl.glGetUniformLocation(self.program, "global_alpha")
        self.i_apply_global_alpha = gl.glGetUniformLocation(
            self.program, "apply_global_alpha"
        )

        self.i_phase = gl.glGetUniformLocation(self.program, "phase")

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
            2,  # size
            gl.GL_FLOAT,  # type
            gl.GL_FALSE,  # normalisation
            0,  # stride
            ctypes.c_void_p(0),  # pointer
        )

        for param in "ST":
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D,
                getattr(gl, "GL_TEXTURE_WRAP_" + param),
                gl.GL_CLAMP_TO_EDGE,
            )
        for param in ("MIN", "MAG"):
            gl.glTexParameteri(
                gl.GL_TEXTURE_2D,
                getattr(gl, "GL_TEXTURE_" + param + "_FILTER"),
                gl.GL_LINEAR,
            )

        gl.glTexParameterfv(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_BORDER_COLOR, np.zeros(4))

        self.i_proj = gl.glGetUniformLocation(self.program, "projection")
        self.i_view = gl.glGetUniformLocation(self.program, "view")
        self.i_model = gl.glGetUniformLocation(self.program, "model")

        # set the rotation matrix to null
        self.set_model(model=np.eye(4).T)

        gl.glUseProgram(0)

        self.phase = [0.0, 0.0]
        self.global_alpha = global_alpha
        self.apply_global_alpha = apply_global_alpha

        self.set_proj(proj=self._proj_mat)

        if model is not None:
            self.set_model(model=model)

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

    def set_img(self, img, srgb=True):

        # load the image
        if not isinstance(img, np.ndarray):
            img = np.flipud(imageio.imread(img))

        (img_h, img_w, img_c) = img.shape

        if img_c == 3:
            # add an alpha channel, if it doesn't have one
            alpha = np.ones_like(img[..., (0,)]) * 255
            img = np.concatenate((img, alpha), axis=-1)

        if srgb:
            fmt = "GL_SRGB_ALPHA"
        else:
            fmt = "GL_RGBA"

        gl.glBindTexture(gl.GL_TEXTURE_2D, self.i_tex)

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,  # target
            0,  # level of detail
            getattr(gl, fmt),
            img_w,  # width
            img_h,  # height
            0,  # border
            gl.GL_RGBA,  # format
            gl.GL_UNSIGNED_BYTE,  # type
            img,
        )

    @property
    def phase(self):
        return self._phase

    @phase.setter
    def phase(self, phase):
        self._phase = phase

        gl.glUseProgram(self.program)
        gl.glUniform2f(self.i_phase, *phase)
        gl.glUseProgram(0)

    @property
    def global_alpha(self):
        return self._global_alpha

    @global_alpha.setter
    def global_alpha(self, global_alpha):
        self._global_alpha = global_alpha

        gl.glUseProgram(self.program)
        gl.glUniform1f(self.i_global_alpha, global_alpha)
        gl.glUseProgram(0)

    @property
    def apply_global_alpha(self):
        return bool(self._apply_global_alpha)

    @apply_global_alpha.setter
    def apply_global_alpha(self, apply_global_alpha):
        if apply_global_alpha:
            self._apply_global_alpha = gl.GL_TRUE
        else:
            self._apply_global_alpha = gl.GL_FALSE

        gl.glUseProgram(self.program)
        gl.glUniform1i(self.i_apply_global_alpha, self._apply_global_alpha)
        gl.glUseProgram(0)

    def draw(self):
        gl.glUseProgram(self.program)

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glBindVertexArray(self.i_vao)
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.i_tex)
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, n_vertices)
        gl.glBindVertexArray(0)
        gl.glUseProgram(0)
