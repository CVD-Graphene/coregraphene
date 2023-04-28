from random import random

from ...system_actions import ManyDeviceControllerAction
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetCurrentPressureVakumetrAdcControllerAction(ManyDeviceControllerAction):

    def _on_get_value(self, value):
        self._controller.current_pressures[self._controller._last_thread_command.device_num] = value

    def _call_function(self, value):
        return float(value)
