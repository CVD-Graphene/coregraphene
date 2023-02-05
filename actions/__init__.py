from ..constants import TABLE_ACTIONS_NAMES
from ..constants import ACTION_NAMES

from conf import settings


def safe_check(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f"{str(e)}"
    return wrapper


class Argument:
    key = None
    arg_type = None
    arg_default = None
    arg_list = None

    @safe_check
    def check(self, value):
        pass


class SccmArgument(Argument):
    arg_type = float
    key = "float"
    decimals = 2
    arg_default = 0.0

    @safe_check
    def check(self, value):
        value = float(value)
        range_list = [0, 200]
        if range_list[0] <= value <= range_list[1]:
            raise Exception(f"SCCM value {value} not in range {range_list}")


class FloatArgument(Argument):
    arg_type = float
    arg_default = 0.0

    @safe_check
    def check(self, value):
        value = float(value)


class IntKeyArgument(Argument):
    key = "int"
    arg_type = int
    arg_default = 0

    @safe_check
    def check(self, value):
        value = int(value)


class FloatKeyArgument(Argument):
    key = "float"
    arg_type = float
    arg_default = 0.0

    @safe_check
    def check(self, value):
        value = float(value)


class GasListArgument(Argument):
    arg_type = list
    arg_list = settings.GAS_LIST

    @safe_check
    def check(self, value):
        value = str(value).strip()
        if value not in self.arg_list:
            raise Exception(f"Gas {value} not in gas list")


class ValveListArgument(Argument):
    arg_type = list
    arg_list = settings.VALVE_LIST

    @safe_check
    def check(self, value):
        value = str(value).strip()
        if value not in self.arg_list:
            raise Exception(f"Valve {value} not in valve list")


class TimeEditArgument(Argument):
    key = "time"

    @safe_check
    def check(self, value):
        pass


class AppAction:
    args_info = []
    args_amount = 0
    key = None
    name = None

    def __init__(self, name=None, key=None, args_info=None):
        if name is not None:
            self.name = name
        if key is not None:
            self.key = key
        if args_info is not None:
            self.args_info = args_info

        self.args_amount = len(self.args_info)

    def check_args(self):
        return None


class TurnOnPumpAction(AppAction):
    name = TABLE_ACTIONS_NAMES.TURN_ON_PUMP
    key = ACTION_NAMES.TURN_ON_PUMP


class OpenValveAction(AppAction):
    name = TABLE_ACTIONS_NAMES.OPEN_VALVE
    key = ACTION_NAMES.OPEN_VALVE
    args_info = [ValveListArgument]


class CloseValveAction(AppAction):
    name = TABLE_ACTIONS_NAMES.CLOSE_VALVE
    key = ACTION_NAMES.CLOSE_VALVE
    args_info = [ValveListArgument]


class CloseAllValvesAction(AppAction):
    name = TABLE_ACTIONS_NAMES.CLOSE_ALL_VALVES
    key = ACTION_NAMES.CLOSE_ALL_VALVES


class SetRrgValueAction(AppAction):
    name = TABLE_ACTIONS_NAMES.SET_RRG_VALUE
    key = ACTION_NAMES.SET_RRG_VALUE
    args_info = [GasListArgument, SccmArgument]


class SetRrgValueWithPauseAction(AppAction):
    name = TABLE_ACTIONS_NAMES.SET_RRG_VALUE_WITH_PAUSE
    key = ACTION_NAMES.SET_RRG_VALUE_WITH_PAUSE
    args_info = [GasListArgument, SccmArgument, TimeEditArgument]


class PumpOutCameraAction(AppAction):
    name = TABLE_ACTIONS_NAMES.PUMP_OUT_CAMERA
    key = ACTION_NAMES.PUMP_OUT_CAMERA
    args_info = [FloatArgument, TimeEditArgument]


class VentilateCameraAction(AppAction):
    name = TABLE_ACTIONS_NAMES.VENTILATE_CAMERA
    key = ACTION_NAMES.VENTILATE_CAMERA
    args_info = [IntKeyArgument, IntKeyArgument]


class RampAction(AppAction):
    name = TABLE_ACTIONS_NAMES.RAMP
    key = ACTION_NAMES.RAMP
    args_info = [FloatKeyArgument, TimeEditArgument]


class SetTemperatureAction(AppAction):
    name = TABLE_ACTIONS_NAMES.SET_TEMPERATURE
    key = ACTION_NAMES.SET_TEMPERATURE
    args_info = [IntKeyArgument, TimeEditArgument]


class PauseAction(AppAction):
    name = TABLE_ACTIONS_NAMES.PAUSE
    key = ACTION_NAMES.PAUSE
    args_info = [TimeEditArgument]


class FullOpenPumpAction(AppAction):
    name = TABLE_ACTIONS_NAMES.FULL_OPEN_PUMP
    key = ACTION_NAMES.FULL_OPEN_PUMP
    args_info = []


class FullClosePumpAction(AppAction):
    name = TABLE_ACTIONS_NAMES.FULL_CLOSE_PUMP
    key = ACTION_NAMES.FULL_CLOSE_PUMP


class StabilizePressureAction(AppAction):
    name = TABLE_ACTIONS_NAMES.STABILIZE_PRESSURE
    key = ACTION_NAMES.STABILIZE_PRESSURE
    args_info = [FloatArgument, TimeEditArgument]


ACTIONS = [
    TurnOnPumpAction(),
    OpenValveAction(),
    CloseValveAction(),
    CloseAllValvesAction(),
    SetRrgValueAction(),
    SetRrgValueWithPauseAction(),
    PumpOutCameraAction(),
    VentilateCameraAction(),
    RampAction(),
    SetTemperatureAction(),
    PauseAction(),
    FullOpenPumpAction(),
    FullClosePumpAction(),
    StabilizePressureAction(),
]


def get_action_by_name(name):
    for i, action in enumerate(ACTIONS):
        if action.name == name:
            return action, i
    return None, 0
