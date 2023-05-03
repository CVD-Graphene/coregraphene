from random import random

from ...system_effects import ControllerEffect
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetCurrentControllerAction(ControllerEffect):

    def _on_get_value(self, value):
        self._controller.current_value = value

    def _call_function(self, value):
        if LOCAL_MODE:
            value = round(random() * 2, 2)
        return float(value)


class GetVoltageControllerAction(ControllerEffect):
    def _on_get_value(self, value):
        self._controller.voltage_value = value

    def _call_function(self, value):
        if LOCAL_MODE:
            value = round(random() * 3, 2)
        return float(value)
