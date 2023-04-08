from random import random

from ...system_actions import ControllerAction
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetCurrentTemperaturePyrometerControllerAction(ControllerAction):

    def _on_get_value(self, value):
        # print("CALL FUNC PYROMETER ACTION:", value)
        self._controller.temperature_value = value

    def _call_function(self, value):
        if LOCAL_MODE:
            value = round(random() * 1000, 1)
        return float(value)
