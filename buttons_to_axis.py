import gremlin
from gremlin.user_plugin import *

import time
import threading
import math

mode = ModeVariable(
    "Mode",
    "The mode to use for this mapping"
)
vjoy_axis = VirtualInputVariable(
    "Output Axis",
    "vJoy axis to use as the output",
    [gremlin.common.InputType.JoystickAxis]
)
btn_e = PhysicalInputVariable(
    "Button Axis Positive",
    "Button which will be mapped to the positive direction of the axis.",
    [gremlin.common.InputType.JoystickButton]
)
btn_w = PhysicalInputVariable(
    "Button Axis Negative",
    "Button which will be mapped to the negative direction of the axis.",
    [gremlin.common.InputType.JoystickButton]
)
update_frequency = FloatVariable(
    "Update Frequency",
    "Axis update, seconds.",
    0.01,
    0.01,
    1.0
)
update_resolution = FloatVariable(
    "Update Resolution",
    "Axis change per tick.",
    0.1,
    -1.0,
    1.0
)

decorator_e = btn_e.create_decorator(mode.value)
decorator_w = btn_w.create_decorator(mode.value)

update_thread   = None
state           = 0

def update_axis_thread(vjoy):
    global state

    freq_value      = update_frequency.value
    res_value       = update_resolution.value

    tick_exec_flag  = True    
    next_tick       = time.time() + freq_value
    
    to_axis_value   = 0.0

    while(True):
        while time.time() < next_tick:
            time.sleep(0.0001)

        device = vjoy[vjoy_axis.value["device_id"]]
        if state == 0:
            device.axis(vjoy_axis.value["input_id"]).value = 0
            #gremlin.util.log(device.axis(vjoy_axis.value["input_id"]).value)            
            break            
        else:
            to_axis_value = max(-1.0, min(1.0, to_axis_value + math.copysign(res_value, state)))
            device.axis(vjoy_axis.value["input_id"]).value = round(to_axis_value, 3)
            #gremlin.util.log(device.axis(vjoy_axis.value["input_id"]).value)
            next_tick += freq_value

    self.join()


def ensure_axis_thread(vjoy):
    global update_thread
    if update_thread is None or update_thread.is_alive() is False:
        update_thread = threading.Thread(target=update_axis_thread, args=(vjoy,))
        update_thread.start()


# positive
@decorator_e.button(btn_e.input_id)
def button_e(event, vjoy):
    global state
    state = 1.0 if event.is_pressed else 0
    ensure_axis_thread(vjoy)


# negative
@decorator_w.button(btn_w.input_id)
def button_w(event, vjoy):
    global state
    state = -1.0 if event.is_pressed else 0
    ensure_axis_thread(vjoy)