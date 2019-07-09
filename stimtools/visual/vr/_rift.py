import os

try:
    import psychxr.ovr as ovr

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

    def __init__(self):

        ovr.initialize()
        ovr.create()

        self.hmd_info = ovr.getHmdInfo()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    @staticmethod
    def close():
        ovr.destroy()
        ovr.shutdown()
