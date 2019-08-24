import os

import numpy as np

import OpenGL.GL as gl

try:
    import psychxr.libovr as ovr
    has_psychxr = True
except ImportError:
    # windows
    if os.name == "nt":
        print("Install `psychxr`")
        raise
    has_psychxr = False

try:
    import pyrr
except ImportError:
    pass


class Rift:
    def __init__(self, monoscopic=True):

        if not monoscopic:
            raise NotImplementedError("Only mono for now")

        ovr.initialize()
        ovr.create()

        try:
            self.hmd_info = ovr.getHmdInfo()

            self.i_left = ovr.EYE_LEFT
            self.i_right = ovr.EYE_RIGHT
            self.i_eyes = (self.i_left, self.i_right)

            symm = self.hmd_info.symmetricEyeFov

            # symmetric for monoscopic
            for (i_eye, eye_fov) in zip(self.i_eyes, symm):
                ovr.setEyeRenderFov(eye=i_eye, fov=eye_fov)

            tex_sizes = [ovr.calcEyeBufferSize(i_eye) for i_eye in self.i_eyes]
            assert tex_sizes[0] == tex_sizes[1]
            (self.tex_size, _) = tex_sizes

            (self.tex_width, self.tex_height) = self.tex_size

            self.viewport = [0, 0, self.tex_size[0], self.tex_size[1]]
            for i_eye in self.i_eyes:
                ovr.setEyeRenderViewport(eye=i_eye, values=self.viewport)

            self.proj_mat = ovr.getEyeProjectionMatrix(0)

            assert np.all(self.proj_mat == ovr.getEyeProjectionMatrix(1))

            ovr.createTextureSwapChainGL(
                ovr.TEXTURE_SWAP_CHAIN0,
                width=self.tex_width,
                height=self.tex_height,
                textureFormat=ovr.FORMAT_R8G8B8A8_UNORM_SRGB,
            )

            for i_eye in self.i_eyes:
                ovr.setEyeColorTextureSwapChain(
                    eye=i_eye, swapChain=ovr.TEXTURE_SWAP_CHAIN0
                )

            ovr.setHighQuality(True)

            gl.glViewport(*self.viewport)

            self.i_fbo = gl.glGenFramebuffers(1)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.i_fbo)

            self.i_rbo = gl.glGenRenderbuffers(1)
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.i_rbo)
            gl.glRenderbufferStorage(
                gl.GL_RENDERBUFFER,
                gl.GL_DEPTH24_STENCIL8,
                self.tex_width,
                self.tex_height,
            )
            gl.glFramebufferRenderbuffer(
                gl.GL_FRAMEBUFFER,
                gl.GL_DEPTH_STENCIL_ATTACHMENT,
                gl.GL_RENDERBUFFER,
                self.i_rbo,
            )

            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        except:
            self.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @staticmethod
    def close():
        ovr.destroyTextureSwapChain(ovr.TEXTURE_SWAP_CHAIN0)
        ovr.destroy()
        ovr.shutdown()


class MockRift:
    def __init__(self, monoscopic=True):

        self.tex_size = [1520] * 2

        (self.tex_width, self.tex_height) = self.tex_size

        self.viewport = [0, 0, self.tex_size[0], self.tex_size[1]]

        self.proj_mat = pyrr.matrix44.create_perspective_projection_matrix(
            fovy=87.4, aspect=1.0, near=0.01, far=100.0
        ).T

        gl.glViewport(*self.viewport)

        self.i_fbo = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    @staticmethod
    def close():
        pass


class Frame:
    def __init__(self, i_frame, i_fbo):

        self._i_frame = i_frame
        self._i_fbo = i_fbo

    def __enter__(self):

        ovr.waitToBeginFrame(self._i_frame)

        abs_time = ovr.getPredictedDisplayTime(self._i_frame)
        (tracking_state, _) = ovr.getTrackingState(abs_time, True)
        (headPose, _) = tracking_state[ovr.TRACKED_DEVICE_TYPE_HMD]
        ovr.calcEyePoses(headPose.pose)

        ovr.beginFrame(self._i_frame)

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._i_fbo)

        gl.glEnable(gl.GL_DEPTH_TEST)

        # "OpenGL will automatically convert the output colors from linear to the sRGB
        # colorspace if, and only if, GL_FRAMEBUFFER_SRGB is enabled"
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

        (_, i_swap) = ovr.getTextureSwapChainCurrentIndex(ovr.TEXTURE_SWAP_CHAIN0)
        (_, i_t) = ovr.getTextureSwapChainBufferGL(ovr.TEXTURE_SWAP_CHAIN0, i_swap)

        gl.glFramebufferTexture2D(
            gl.GL_DRAW_FRAMEBUFFER,  # target
            gl.GL_COLOR_ATTACHMENT0,  # attachment
            gl.GL_TEXTURE_2D,  # tex target
            i_t,  # texture
            0,  # level
        )

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        view = ovr.getEyeViewMatrix(0)

        return view

    def __exit__(self, exc_type, exc_value, traceback):

        # only wind up properly if there hasn't been an exception
        if exc_type is None:

            ovr.commitTextureSwapChain(ovr.TEXTURE_SWAP_CHAIN0)

            gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)

            ovr.endFrame(self._i_frame)

            gl.glDisable(gl.GL_FRAMEBUFFER_SRGB)

            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_SCISSOR_TEST)


class MockFrame:
    def __init__(self, i_frame, i_fbo):

        self._i_frame = i_frame
        self._i_fbo = i_fbo

    def __enter__(self):

        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

        view = np.eye(4)

        return view

    def __exit__(self, exc_type, exc_value, traceback):

        if exc_type is None:
            gl.glDisable(gl.GL_FRAMEBUFFER_SRGB)
