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

    def _check(self, value):
        self.prepare_value(value)

    @staticmethod
    def prepare_value(value):
        return value


class FloatArgument(Argument):
    arg_type = float
    arg_default = 0.0

    @staticmethod
    def prepare_value(value):
        return float(value)


class SccmArgument(FloatArgument):
    key = "float"
    decimals = 2
    max_sccm = settings.MAX_DEFAULT_SCCM_VALUE

    def update_max_sccm(self, max_sccm):
        self.max_sccm = max_sccm

    def _check(self, value):
        value = self.prepare_value(value)
        # range_list = [0, self.max_sccm]
        # if not range_list[0] <= value <= range_list[1]:
        #     raise Exception(f"SCCM value {value} not in range {range_list}")

    @staticmethod
    def prepare_value(value):
        return float(value)


class IntKeyArgument(Argument):
    key = "int"
    arg_type = int
    arg_default = 0

    @staticmethod
    def prepare_value(value):
        return int(value)


class PositiveIntKeyArgument(IntKeyArgument):
    def _check(self, value):
        value = self.prepare_value(value)
        if value < 0:
            raise Exception(f"Int value {value} must be >= 0")


class FloatKeyArgument(Argument):
    key = "float"
    arg_type = float
    arg_default = 0.0

    @staticmethod
    def prepare_value(value):
        return float(value)


class PositiveFloatKeyArgument(FloatKeyArgument):
    key = "float"
    arg_type = float
    arg_default = 0.0

    def _check(self, value):
        value = self.prepare_value(value)
        if value < 0:
            raise Exception(f"Float value {value} must be >= 0")


class GasListArgument(Argument):
    arg_type = list
    arg_list = settings.GAS_LIST

    def _check(self, value):
        value = self.prepare_value(value)
        if value not in self.arg_list:
            raise Exception(f"Gas {value} not in gas list")

    @staticmethod
    def prepare_value(value):
        return str(value).strip()


class ValveListArgument(Argument):
    arg_type = list
    arg_list = settings.VALVE_LIST

    def _check(self, value):
        value = self.prepare_value(value)
        if value not in self.arg_list:
            raise Exception(f"Valve {value} not in valve list")

    @staticmethod
    def prepare_value(value):
        return str(value).strip()


class TimeEditArgument(Argument):
    key = "time"

    @staticmethod
    def prepare_value(value):
        if type(value) in [int, float]:
            return value
        value = str(value)
        ints = list(map(int, value.strip().split(':')))
        if len(ints) == 1:
            return ints[0]
        return ints[0] * 60 + ints[1]


def get_total_seconds_from_time_arg(time_arg):
    mins, secs = list(map(int, time_arg.strip().split(':')))
    return mins * 60 + secs
