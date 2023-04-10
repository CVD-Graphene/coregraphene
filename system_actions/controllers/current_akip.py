from random import random

from ...system_actions import ControllerAction
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetCurrentControllerAction(ControllerAction):

    def _on_get_value(self, value):
        self._controller.current_value = value

    def _call_function(self, value):
        # if LOCAL_MODE:
        #     value = round(random() * 1, 2)
        return float(value)


class GetVoltageControllerAction(ControllerAction):
    def _on_get_value(self, value):
        self._controller.voltage_value = value

    def _call_function(self, value):
        return float(value)
