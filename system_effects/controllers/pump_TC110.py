from random import random

from ...system_effects import ControllerEffect
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetActualSpeedPumpTC110ControllerEffect(ControllerEffect):
    def _on_get_value(self, value):
        self._controller.actual_speed = value

    def _call_function(self, value):
        if LOCAL_MODE:
            return 0.0
        return float(value)
