import os
import contextlib

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

import easygui


class Rift:
    def __init__(self, msaa=1, require_controller=False):

        self._msaa = msaa
        self._require_controller = require_controller

        self.hmd_info = None
        self.tex_width = self.tex_height = self.tex_size = None
        self.proj_mat = None
        self.i_fbo = self.i_rbo = None

        self.yaw = self.pitch = self.roll = None

        self.ypr = None

        self._i_frame = 0

        self.nests = 0

    def __enter__(self):

        self.nests += 1

        if self.nests > 1:
            return self

        ovr.initialize()
        ovr.create()

        # get response devices
        controllers_ok = False
        while not controllers_ok:

            controllers = ovr.getConnectedControllerTypes()

            if len(controllers) == 0:
                if self._require_controller:
                    try_again = easygui.ccbox(
                        msg="Pair a touch device", choices=["Try again", "Cancel"]
                    )
                    if not try_again:
                        raise ValueError("User cancelled")
                else:
                    self._controller = None
                    controllers_ok = True
            elif len(controllers) == 1:
                (self._controller,) = controllers
                controllers_ok = True
            else:
                use_left_controller = easygui.boolbox(
                    msg="Which controller?", choices=["Left", "Right"]
                )
                if use_left_controller:
                    controller_id = ovr.CONTROLLER_TYPE_LTOUCH
                else:
                    controller_id = ovr.CONTROLLER_TYPE_RTOUCH
                self._controller = controllers[controllers.index(controller_id)]
                controllers_ok = True

        self._last_thumb = 0.0

        self.hmd_info = ovr.getHmdInfo()

        i_left = ovr.EYE_LEFT
        i_right = ovr.EYE_RIGHT
        i_eyes = (i_left, i_right)

        symm = self.hmd_info.symmetricEyeFov

        # symmetric for monoscopic
        for (i_eye, eye_fov) in zip(i_eyes, symm):
            ovr.setEyeRenderFov(eye=i_eye, fov=eye_fov)

        tex_sizes = [ovr.calcEyeBufferSize(i_eye) for i_eye in i_eyes]
        assert tex_sizes[0] == tex_sizes[1]
        (self.tex_size, _) = tex_sizes

        (self.tex_width, self.tex_height) = self.tex_size

        self.viewport = [0, 0, self.tex_size[0], self.tex_size[1]]
        for i_eye in i_eyes:
            ovr.setEyeRenderViewport(eye=i_eye, values=self.viewport)

        self.proj_mat = ovr.getEyeProjectionMatrix(0)

        assert np.all(self.proj_mat == ovr.getEyeProjectionMatrix(1))

        ovr.createTextureSwapChainGL(
            ovr.TEXTURE_SWAP_CHAIN0,
            width=self.tex_width,
            height=self.tex_height,
            textureFormat=ovr.FORMAT_R8G8B8A8_UNORM_SRGB,
        )

        for i_eye in i_eyes:
            ovr.setEyeColorTextureSwapChain(
                eye=i_eye, swapChain=ovr.TEXTURE_SWAP_CHAIN0
            )

        ovr.setHighQuality(True)

        gl.glViewport(*self.viewport)

        # generate the MSAA buffer
        if self._msaa > 1:

            self.i_msaa_fbo = gl.glGenFramebuffers(1)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.i_msaa_fbo)

            self.i_msaa_rbo = gl.glGenRenderbuffers(1)
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.i_msaa_rbo)
            gl.glRenderbufferStorageMultisample(
                gl.GL_RENDERBUFFER,
                self._msaa,
                gl.GL_SRGB8_ALPHA8,
                self.tex_width,
                self.tex_height,
            )
            gl.glFramebufferRenderbuffer(
                gl.GL_FRAMEBUFFER,
                gl.GL_COLOR_ATTACHMENT0,
                gl.GL_RENDERBUFFER,
                self.i_msaa_rbo,
            )
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)

            self.i_msaa_depth_rbo = gl.glGenRenderbuffers(1)
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.i_msaa_depth_rbo)
            gl.glRenderbufferStorageMultisample(
                gl.GL_RENDERBUFFER,
                self._msaa,
                gl.GL_DEPTH24_STENCIL8,
                self.tex_width,
                self.tex_height,
            )
            gl.glFramebufferRenderbuffer(
                gl.GL_FRAMEBUFFER,
                gl.GL_DEPTH_ATTACHMENT,
                gl.GL_RENDERBUFFER,
                self.i_msaa_depth_rbo,
            )
            gl.glFramebufferRenderbuffer(
                gl.GL_FRAMEBUFFER,
                gl.GL_STENCIL_ATTACHMENT,
                gl.GL_RENDERBUFFER,
                self.i_msaa_depth_rbo,
            )
            gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)
            gl.glClear(gl.GL_STENCIL_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        self.i_fbo = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.i_fbo)

        self.i_rbo = gl.glGenRenderbuffers(1)
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, self.i_rbo)
        gl.glRenderbufferStorage(
            gl.GL_RENDERBUFFER, gl.GL_DEPTH24_STENCIL8, self.tex_width, self.tex_height
        )
        gl.glFramebufferRenderbuffer(
            gl.GL_FRAMEBUFFER,
            gl.GL_DEPTH_STENCIL_ATTACHMENT,
            gl.GL_RENDERBUFFER,
            self.i_rbo,
        )

        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        return self

    def __exit__(self, exc_type, exc_value, traceback):

        self.nests -= 1

        if self.nests == 0:
            ovr.destroyTextureSwapChain(ovr.TEXTURE_SWAP_CHAIN0)
            ovr.destroy()
            ovr.shutdown()

    @contextlib.contextmanager
    def frame(self):

        ovr.waitToBeginFrame(self._i_frame)

        abs_time = ovr.getPredictedDisplayTime(self._i_frame)
        tracking_state = ovr.getTrackingState(abs_time, True)
        ovr.calcEyePoses(tracking_state.headPose.thePose)

        self.ypr = tracking_state.headPose.thePose.getYawPitchRoll()

        (self.yaw, self.pitch, self.roll) = self.ypr

        ovr.beginFrame(self._i_frame)

        (_, i_swap) = ovr.getTextureSwapChainCurrentIndex(ovr.TEXTURE_SWAP_CHAIN0)
        (_, i_t) = ovr.getTextureSwapChainBufferGL(ovr.TEXTURE_SWAP_CHAIN0, i_swap)

        if self._msaa == 1:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.i_fbo)
            gl.glFramebufferTexture2D(
                gl.GL_DRAW_FRAMEBUFFER,  # target
                gl.GL_COLOR_ATTACHMENT0,  # attachment
                gl.GL_TEXTURE_2D,  # tex target
                i_t,  # texture
                0,  # level
            )
        else:
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.i_msaa_fbo)
            gl.glEnable(gl.GL_MULTISAMPLE)

        # "OpenGL will automatically convert the output colors from linear to the sRGB
        # colorspace if, and only if, GL_FRAMEBUFFER_SRGB is enabled"
        gl.glEnable(gl.GL_FRAMEBUFFER_SRGB)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        view = ovr.getEyeViewMatrix(0)

        yield view

        if self._msaa > 1:

            gl.glBindFramebuffer(gl.GL_READ_FRAMEBUFFER, self.i_msaa_fbo)
            gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, self.i_fbo)

            gl.glFramebufferTexture2D(
                gl.GL_DRAW_FRAMEBUFFER,
                gl.GL_COLOR_ATTACHMENT0,
                gl.GL_TEXTURE_2D,
                i_t,
                0,
            )

            gl.glBlitFramebuffer(
                0,
                0,
                self.tex_width,
                self.tex_height,
                0,
                0,
                self.tex_width,
                self.tex_height,
                gl.GL_COLOR_BUFFER_BIT,
                gl.GL_NEAREST,
            )

            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        ovr.commitTextureSwapChain(ovr.TEXTURE_SWAP_CHAIN0)

        gl.glBindFramebuffer(gl.GL_DRAW_FRAMEBUFFER, 0)

        ovr.endFrame(self._i_frame)

        gl.glDisable(gl.GL_FRAMEBUFFER_SRGB)

        gl.glDisable(gl.GL_DEPTH_TEST)
        gl.glDisable(gl.GL_SCISSOR_TEST)

        self._i_frame += 1

    def update_controller(
        self, thumb_threshold=0.8, min_t_interval_s=0.5, any_button=False
    ):

        if self._controller is not None:

            ovr.updateInputState(self._controller)

            buttons_to_check = [ovr.BUTTON_A, ovr.BUTTON_X]

            if any_button:
                buttons_to_check += [ovr.BUTTON_B, ovr.BUTTON_Y]

            # `getButton` can only check for one button at a time
            # the docs about ORing are for simultaneous presses
            resp_status = [
                ovr.getButton(self._controller, button_to_check, "pressed")
                for button_to_check in buttons_to_check
            ]

            self.button = any([button_pressed for (button_pressed, _) in resp_status])

            (_, time) = resp_status[-1]

            (left_touch, right_touch) = ovr.getThumbstickValues(self._controller, False)

            self.thumb_x = np.array([left_touch[0], right_touch[0]])
            self.thumb_y = np.array([left_touch[1], right_touch[1]])

            if (time - self._last_thumb) > min_t_interval_s:
                self.thumb_left = np.any(self.thumb_x < -(thumb_threshold))
                self.thumb_right = np.any(self.thumb_x > thumb_threshold)
                if self.thumb_left or self.thumb_right:
                    self._last_thumb = time
            else:
                self.thumb_left = self.thumb_right = False
