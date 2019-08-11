import os
import numpy as np

try:
    import psychxr.libovr as ovr
except ImportError:
    # windows
    if os.name == "nt":
        print("Install `psychxr`")
        raise


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

            symm = self.hmd_info.symmetricEyeFov[0]
            default = self.hmd_info.defaultEyeFov[0]

            fov = np.copy(default)
            fov[2:] = symm[2:]

            # symmetric for monoscopic
            for (i_eye, eye_fov) in zip(self.i_eyes, symm):
                ovr.setEyeRenderFov(eye=i_eye, fov=fov)

            tex_sizes = [ovr.calcEyeBufferSize(i_eye) for i_eye in self.i_eyes]
            assert tex_sizes[0] == tex_sizes[1]
            (self.tex_size, _) = tex_sizes

            (self.tex_width, self.tex_height) = self.tex_size

            self.viewport = [0, 0, self.tex_size[0], self.tex_size[1]]
            for i_eye in self.i_eyes:
                ovr.setEyeRenderViewport(eye=i_eye, values=self.viewport)

            self.proj_mat = ovr.getEyeProjectionMatrix(0)

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

        # do these need to be done each frame?
        (_, i_swap) = ovr.getTextureSwapChainCurrentIndex(
            ovr.TEXTURE_SWAP_CHAIN0,
        )
        (_, i_t) = ovr.getTextureSwapChainBufferGL(
            ovr.TEXTURE_SWAP_CHAIN0, i_swap
        )

        gl.glFramebufferTexture2D(
            gl.GL_DRAW_FRAMEBUFFER,  # target
            gl.GL_COLOR_ATTACHMENT0,  # attachment
            gl.GL_TEXTURE_2D,  # tex target
            i_t,  # texture
            0,  # level
        )

        # these are really window operations
        #gl.glViewport(*(rift.viewport))
        #gl.glClearColor(*(win.colour + (1.0, )))
        #gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        view = ovr.getEyeViewMatrix(0)

        return view

    def __exit__(self, exc_type, exc_value, traceback):

        # only wind up properly if there hasn't been an exception
        if exc_type is None:

            ovr.commitTextureSwapChain(ovr.TEXTURE_SWAP_CHAIN0)

            gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)

            ovr.endFrame(self._i_frame)
