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
