import collections

try:
    import glfw
except ImportError:
    print("Fatal error: no 'glfw' package found. Consider `pip install glfw`.")

import OpenGL.GL as gl


KEYCODE_TO_KEY = {
    keycode: "_".join(key.split("_")[1:]).lower()
    for (key, keycode) in vars(glfw).items()
    if key.startswith("KEY_")
}

MODCODE_TO_KEY = {
    modcode: "_".join(key.split("_")[1:]).lower()
    for (key, modcode) in vars(glfw).items()
    if key.startswith("MOD_")
}

Keypress = collections.namedtuple(
    typename="Keypress", field_names=["name", "time", "mod"]
)


class Window:
    def __init__(
        self,
        size_pix=(800, 800),
        colour=(0, 0, 0),
        event_buffer_size=20,
        gamma=None,
        close_on_exit=True,
        global_quit=True,
    ):

        self._global_quit = global_quit

        self.colour = tuple(colour)

        self.close_on_exit = close_on_exit

        self._event_buffer = collections.deque(maxlen=event_buffer_size)

        glfw.init()

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, 1)

        glfw.window_hint(glfw.DOUBLEBUFFER, glfw.TRUE)

        self.monitor = glfw.get_primary_monitor()

        self._orig_gamma = glfw.get_gamma_ramp(self.monitor)

        if gamma is not None:
            glfw.set_gamma(monitor=self.monitor, gamma=gamma)

        self.win = glfw.create_window(
            width=size_pix[0],
            height=size_pix[1],
            title="window",
            monitor=None,
            share=None,
        )

        glfw.make_context_current(self.win)

        glfw.swap_interval(0)

        glfw.set_key_callback(self.win, self.key_event_callback)

        glfw.set_window_close_callback(self.win, self.window_close_callback)

        gl.glClearColor(*(self.colour + (1.0,)))

        self.flip()

        glfw.set_time(0.0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None or self.close_on_exit:
            self.close()

    def close(self):
        glfw.set_gamma_ramp(monitor=self.monitor, ramp=self._orig_gamma)
        glfw.destroy_window(self.win)
        glfw.terminate()

    def flip(self):
        glfw.swap_buffers(self.win)
        glfw.poll_events()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    def window_close_callback(self, window):
        self.close()

    def get_time(self):
        return glfw.get_time()

    def key_event_callback(self, window, key, scancode, action, mods):

        time = self.get_time()

        if action == glfw.PRESS:

            if mods == 0:
                mod = None
            else:
                mod = MODCODE_TO_KEY[mods]

            keypress = Keypress(name=KEYCODE_TO_KEY[key], time=time, mod=mod)

            if keypress.name == "q" and self._global_quit:
                raise ValueError("User quit")

            self._event_buffer.append(keypress)

    def wait_keys(self):

        self._event_buffer.clear()

        while not self._event_buffer:
            glfw.wait_events()

        return self.get_keys()

    def get_keys(self):

        events = tuple(self._event_buffer)

        self._event_buffer.clear()

        return events
