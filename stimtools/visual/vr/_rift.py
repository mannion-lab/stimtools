import os
import numpy as np
try:
    import psychxr.libovr as ovr

except ImportError:

    # windows
    if os.name == "nt":
        print("Install `psychxr`")
        raise

    print("`psychxr` unavailable; using a dummy")


class DummyOvr:

    @staticmethod
    def initialize():
        pass

    @staticmethod
    def create():
        pass

    @staticmethod
    def getHmdInfo():
        pass

    @staticmethod
    def destroy():
        pass

    @staticmethod
    def shutdown():
        pass

try:
    ovr
except NameError:
    ovr = DummyOvr


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
            
            ovr.createTextureSwapChainGL(
                ovr.TEXTURE_SWAP_CHAIN0,
                width=self.tex_width,
                height=self.tex_height,
                textureFormat=ovr.FORMAT_R8G8B8A8_UNORM_SRGB,
            )
            
            for i_eye in self.i_eyes:
                ovr.setEyeColorTextureSwapChain(eye=i_eye, swapChain=ovr.TEXTURE_SWAP_CHAIN0)
            
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
