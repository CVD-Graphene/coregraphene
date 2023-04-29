import random
from time import sleep
from ...conf import settings

from ..communicators import SerialAsciiCommunicator, BaseSerialAsciiCommunicator
from ...constants.components import BACK_PRESSURE_VALVE_CONSTANTS
from .base import AbstractDevice

LOCAL_MODE = settings.LOCAL_MODE

PRESSURE_MARGIN = BACK_PRESSURE_VALVE_CONSTANTS.MAX_PRESSURE_BORDER - \
                  BACK_PRESSURE_VALVE_CONSTANTS.MIN_PRESSURE_BORDER


class BackPressureValveDevice(AbstractDevice):
    communicator_class = BaseSerialAsciiCommunicator
    local_target_pressure_percent = 0.0

    def get_value_with_waiting(self):
        """For testing"""
        self.exec_command(command="MV", value="00")
        sleep(0.5)
        r = self.read()
        print("Read accurate vakumetr value:", r)  # , "KW", self.kwargs)
        return r

    def _percent_to_pressure(self, percent):
        return percent / 100 * PRESSURE_MARGIN + \
               BACK_PRESSURE_VALVE_CONSTANTS.MIN_PRESSURE_BORDER

    def _pressure_to_percent(self, pressure):
        pressure = max(0, min(BACK_PRESSURE_VALVE_CONSTANTS.MAX_PRESSURE_BORDER, pressure))
        return (pressure - BACK_PRESSURE_VALVE_CONSTANTS.MIN_PRESSURE_BORDER) / \
               PRESSURE_MARGIN * 100

    def check_current_position(self):
        pass

    def _preprocessing_value(self, command=None, value=None):
        print("BACK PRESSURE PREPROC:::", command, value)
        if command == BACK_PRESSURE_VALVE_CONSTANTS.WRITE_TARGET_PRESSURE:
            value = round(self._pressure_to_percent(value), 2)
            self.local_target_pressure_percent = value
            command = f"{command}+{value}"
            print("[] Send target command [BACK VALVE]:", command)
            # return ans
        return f"{command}\r"

    def _postprocessing_value(self, value=None):
        v = str(value)
        if v:
            v = v.strip()
        print("BACK PRESSURE POSTPROC:!:!:", v)
        if LOCAL_MODE:
            value = "0\r"
        if not value:
            return None
        value = value.strip()
        if self._last_command == BACK_PRESSURE_VALVE_CONSTANTS.READ_PRESSURE:
            if LOCAL_MODE:
                value = f"P+{round(random.random() * 100, 2)}"
            return self._percent_to_pressure(float(value[2:]))
        elif self._last_command == BACK_PRESSURE_VALVE_CONSTANTS.READ_TARGET_PRESSURE:
            if LOCAL_MODE:
                value = f"S1+{self.local_target_pressure_percent}"
            return self._percent_to_pressure(float(value[3:]))
        elif self._last_command == BACK_PRESSURE_VALVE_CONSTANTS.READ_VALVE_POSITION_PERCENT:
            if LOCAL_MODE:
                value = f"V+{round(random.random() * 100, 2)}"
            return float(value[2:])

        return None
