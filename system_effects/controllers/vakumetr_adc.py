from random import random

from ...system_effects import ManyDeviceControllerEffect
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetCurrentPressureVakumetrAdcControllerEffect(ManyDeviceControllerEffect):

    def _on_get_value(self, value):
        # print("Vakumetr value:", self._controller._last_thread_command.device_num, value)
        self._controller.current_pressures[self._controller._last_thread_command.device_num] = value

    def _call_function(self, value):
        return float(value)
