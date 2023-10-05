from random import random

from ...system_effects import ControllerEffect
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetCurrentPressureVakumetrControllerEffect(ControllerEffect):

    def _on_get_value(self, value):
        # print("CALL FUNC VAKUMETR ACTION:", value)
        self._controller.vakumetr_value = value

    def _call_function(self, value):
        if LOCAL_MODE:
            value = round(random() * 100, 1)
        return float(value)


class GetCurrentPressureBHVakumetrControllerEffect(ControllerEffect):
    def _on_get_value(self, value):
        self._controller.current_pressure = value

    def _call_function(self, value):
        # print('====== BH VAKUM _call_function', value)
        if LOCAL_MODE:
            return round(random() * 100, 1)
        if type(value) == list:
            value = value[0]
        return self._process_voltage_value(float(value))

    def _process_voltage_value(self, value):
        # device_num = self._controller._last_thread_command.kwargs['arg1']
        return 1.0 * 10 ** (0.778 * (value * 6.95 - 6.143))
