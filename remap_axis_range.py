import gremlin
from gremlin.spline import CubicSpline
from gremlin.user_plugin import *


mode = ModeVariable(
    "Mode",
    "The mode to use for this mapping"
)
vjoy_axis = VirtualInputVariable(
    "Output Axis",
    "vJoy axis to use as the output",
    [gremlin.common.InputType.JoystickAxis]
)
real_axis = PhysicalInputVariable(
    "Axis to Remap",
    "Device axis which will be remapped to range.",
    [gremlin.common.InputType.JoystickAxis]
)
lower_bound = FloatVariable(
    "Lower Range Bound",
    "Lower bound value for the remapped range.",
    0.0,
    -1.0,
    1.0
)
upper_bound = FloatVariable(
    "Upper Range Bound",
    "Upper bound value for the remapped range.",
    1.0,
    -1.0,
    1.0
)
update_curve = StringVariable(
    "Response Curve",
    "Interpolation curve: LINEAR (default), EASEIN, EASEOUT",
    "LINEAR"
)

decorator_a = real_axis.create_decorator(mode.value)

curves          = {
    "LINEAR": CubicSpline([
        (-1.0, -1.0),
        ( 0.0,  0.0),
        ( 1.0,  1.0)
    ]),
    "EASEIN": CubicSpline([
        (-1.0, -1.0),
        (-0.5, -0.25),
        ( 0.0,  0.0),
        ( 0.5,  0.25),
        ( 1.0,  1.0)
    ]),
    "EASEOUT": CubicSpline([
        (-1.0, -1.0),
        (-0.25, -0.5),
        ( 0.0,  0.0),
        ( 0.25,  0.5),
        ( 1.0,  1.0)
    ]),
    }

# LINEAR
#           =
#      =
# =

# EASEIN
#           =
#          =
#      ==
#   =
# =

# EASEOUT
#          ==
#       =
#      =
#     =
# ==

@decorator_a.axis(real_axis.input_id)
def axis_remap(event, vjoy):
    new_max      = upper_bound.value
    new_min      = lower_bound.value

    if new_max <= new_min:
        #gremlin.util.log("remap_axis_range is not active; max is less than or equal to lower bound.")
        return

    device          = vjoy[vjoy_axis.value["device_id"]]
    curve_axis_val  = curves[ update_curve.value ]( event.value )
    remapped_value  = (((curve_axis_val - -1.0) * (new_max - new_min)) / (1.0 - -1.0)) + new_min
    #gremlin.util.log("{} => {}".format(event.value, round(remapped_value, 3)))

    device.axis(vjoy_axis.value["input_id"]).value = round(remapped_value, 5)

