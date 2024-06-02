import win32gui
import re
import time
import gremlin
from gremlin.user_plugin import *

mode = ModeVariable(
    "Mode",
    "The mode to use for this mapping"
)
watch_axis = PhysicalInputVariable(
    "Axis to Watch",
    "Device axis which will trigger activate.",
    [gremlin.common.InputType.JoystickAxis]
)
watch_btn = PhysicalInputVariable(
    "Button Axis Positive",
    "Button which will be mapped to the positive direction of the axis.",
    [gremlin.common.InputType.JoystickButton]
)
window_name = StringVariable(
    "Window Name",
    "",
    ""
)
axis_frequency = FloatVariable(
    "Axis Update Frequency",
    "Interval, 0.0-1.0 seconds.",
    1.00,
    0.01,
    1.00
)

decorator_a = watch_axis.create_decorator(mode.value)
decorator_b = watch_btn.create_decorator(mode.value)

class WindowMgr:
    """https://stackoverflow.com/questions/2090464/python-window-activation"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        if self._handle is None:
            win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        if self._handle is not None:
            try:
                win32gui.SetForegroundWindow(self._handle)
            except:
                # Invalid window handle; no handle or no longer valid, reset state
                self._handle = None
                return

w = WindowMgr()
t = time.time()

def focus_window():
    global w
    w.find_window_wildcard(r".*" + re.escape(window_name.value) + r".*")
    w.set_foreground()

@decorator_a.axis(watch_axis.input_id)
def axis_callback(event, vjoy):
    global t
    d = time.time()
    if d > t:
        focus_window()
        t = d + axis_frequency.value

@decorator_b.button(watch_btn.input_id)
def button_callback(event, vjoy):
    if event.is_pressed:
        focus_window()