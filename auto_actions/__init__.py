from abc import abstractmethod

# from ..constants import TABLE_ACTIONS_NAMES
# from ..constants import ACTIONS_NAMES

from ..conf import settings
# from ..utils.auto_actions import safe_check

ACTIONS_NAMES = settings.ACTIONS_NAMES
TABLE_ACTIONS_NAMES = settings.TABLE_ACTIONS_NAMES


class Argument:
    key = None
    arg_type = None
    arg_default = None
    arg_list = None

    def __init__(self):
        pass

    def check(self, value):
        # print("CHECK START:", value)
        try:
            return self._check(value)
        except Exception as e:
            return f"{str(e)}"

    @abstractmethod
    def _check(self, value):
        pass


class FloatArgument(Argument):
    arg_type = float
    arg_default = 0.0

    def _check(self, value):
        value = float(value)


class SccmArgument(FloatArgument):
    key = "float"
    decimals = 2

    def _check(self, value):
        value = float(value)
        range_list = [0, settings.MAX_SCCM_VALUE]
        if not range_list[0] <= value <= range_list[1]:
            raise Exception(f"SCCM value {value} not in range {range_list}")


class IntKeyArgument(Argument):
    key = "int"
    arg_type = int
    arg_default = 0

    def _check(self, value):
        value = int(value)


class PositiveIntKeyArgument(IntKeyArgument):
    def _check(self, value):
        value = int(value)
        if value < 0:
            raise Exception(f"Int value {value} must be >= 0")


class FloatKeyArgument(Argument):
    key = "float"
    arg_type = float
    arg_default = 0.0

    def _check(self, value):
        value = float(value)


class PositiveFloatKeyArgument(Argument):
    key = "float"
    arg_type = float
    arg_default = 0.0

    def _check(self, value):
        value = float(value)
        if value < 0:
            raise Exception(f"Float value {value} must be >= 0")


class GasListArgument(Argument):
    arg_type = list
    arg_list = settings.GAS_LIST

    def _check(self, value):
        value = str(value).strip()
        if value not in self.arg_list:
            raise Exception(f"Gas {value} not in gas list")


class ValveListArgument(Argument):
    arg_type = list
    arg_list = settings.VALVE_LIST

    def _check(self, value):
        value = str(value).strip()
        if value not in self.arg_list:
            raise Exception(f"Valve {value} not in valve list")


class TimeEditArgument(Argument):
    key = "time"

    def _check(self, value):
        pass


class AppAction:
    args_info = []
    _args_amount = 0
    key = None
    name = None

    # def __init__(self, name: str = None, key: str = None, args_info: list = None):
    #     self.name = name
    #     self.key = key
    #     self.args_info = args_info or []
    #     self.args_amount = len(self.args_info)

    def __init__(self):
        self._args_amount = len(self.args_info)

    def set_functions(self,
                      system=None,
                      get_current_recipe_state=None,
                      **kwargs):
        self.system = system
        self.get_current_recipe_state = get_current_recipe_state

    @abstractmethod
    def action(self, *args, **kwargs):
        pass

    @property
    def args_amount(self):
        if self._args_amount == 0:
            self._args_amount = len(self.args_info)
        return self._args_amount

    def check_args(self):
        return None


# class TurnOnPumpAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.TURN_ON_PUMP
#     key = ACTIONS_NAMES.TURN_ON_PUMP


# class OpenValveAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.OPEN_VALVE
#     key = ACTIONS_NAMES.OPEN_VALVE
#     args_info = [ValveListArgument]
#
#
# class CloseValveAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.CLOSE_VALVE
#     key = ACTIONS_NAMES.CLOSE_VALVE
#     args_info = [ValveListArgument]
#
#
# class CloseAllValvesAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.CLOSE_ALL_VALVES
#     key = ACTIONS_NAMES.CLOSE_ALL_VALVES


# class SetRrgSccmValueAction(AppAction):
#     """
#     Установить значение sccm для ррг
#     """
#     name = TABLE_ACTIONS_NAMES.SET_RRG_VALUE
#     key = ACTIONS_NAMES.SET_RRG_VALUE
#     args_info = [GasListArgument, SccmArgument]


# class SetRrgSccmValueWithPauseAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.SET_RRG_VALUE_WITH_PAUSE
#     key = ACTIONS_NAMES.SET_RRG_VALUE_WITH_PAUSE
#     args_info = [GasListArgument, SccmArgument, TimeEditArgument]


# class PumpOutCameraAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.PUMP_OUT_CAMERA
#     key = ACTIONS_NAMES.PUMP_OUT_CAMERA
#     args_info = [FloatArgument, TimeEditArgument]


# class VentilateCameraAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.VENTILATE_CAMERA
#     key = ACTIONS_NAMES.VENTILATE_CAMERA
#     args_info = [IntKeyArgument, IntKeyArgument]


# class RampAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.RAMP
#     key = ACTIONS_NAMES.RAMP
#     args_info = [FloatKeyArgument, TimeEditArgument]


# class SetTemperatureInTimeAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.SET_TEMPERATURE_IN_TIME
#     key = ACTIONS_NAMES.SET_TEMPERATURE_IN_TIME
#     args_info = [IntKeyArgument, TimeEditArgument]


# class SetTemperatureAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.SET_TEMPERATURE
#     key = ACTIONS_NAMES.SET_TEMPERATURE
#     args_info = [IntKeyArgument]


# class PauseAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.PAUSE
#     key = ACTIONS_NAMES.PAUSE
#     args_info = [TimeEditArgument]


# class FullOpenPumpAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.FULL_OPEN_PUMP
#     key = ACTIONS_NAMES.FULL_OPEN_PUMP
#     args_info = []


# class FullClosePumpAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.FULL_CLOSE_PUMP
#     key = ACTIONS_NAMES.FULL_CLOSE_PUMP


# class StabilizePressureAction(AppAction):
#     name = TABLE_ACTIONS_NAMES.STABILIZE_PRESSURE
#     key = ACTIONS_NAMES.STABILIZE_PRESSURE
#     args_info = [FloatArgument, TimeEditArgument]
