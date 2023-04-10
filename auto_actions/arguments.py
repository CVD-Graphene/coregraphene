from abc import abstractmethod
from ..conf import settings


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
    max_sccm = settings.MAX_DEFAULT_SCCM_VALUE

    def update_max_sccm(self, max_sccm):
        self.max_sccm = max_sccm

    def _check(self, value):
        value = float(value)
        # range_list = [0, self.max_sccm]
        # if not range_list[0] <= value <= range_list[1]:
        #     raise Exception(f"SCCM value {value} not in range {range_list}")


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


def get_total_seconds_from_time_arg(time_arg):
    mins, secs = list(map(int, time_arg.strip().split(':')))
    return mins * 60 + secs
