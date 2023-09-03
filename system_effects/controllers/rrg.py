from random import random

from ...system_effects import ManyDeviceControllerEffect
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetCurrentFlowRrgControllerEffect(ManyDeviceControllerEffect):

    def _on_get_value(self, value):
        # print("CALL FUNC CURRENT FLOW CONTROLLER 2:", value)
        self._controller.current_sccms[self._controller._last_thread_command.device_num] = value

    def _call_function(self, value):
        max_sccm = self._controller.get_max_sccm_device(
            device_num=self._controller._last_thread_command.device_num)
        if LOCAL_MODE:
            value = random() * 100 * 100
        value = float(value) / (100 * 100) * max_sccm
        # print("CALL FUNC CURRENT FLOW CONTROLLER:", value)
        return value


class GetCurrentSccmRrgAdcControllerEffect(ManyDeviceControllerEffect):

    def _on_get_value(self, value):
        # print("CALL FUNC CURRENT FLOW CONTROLLER 2:", value)
        self._controller.current_sccms[self._controller._last_thread_command.device_num] = value

    def _call_function(self, value):
        # max_sccm = self._controller.get_max_sccm_device(
        #     device_num=self._controller._last_thread_command.device_num)
        # if LOCAL_MODE:
        #     value = random() * 100 * 100
        # value = float(value) / (100 * 100) * max_sccm
        # print("CALL FUNC CURRENT FLOW CONTROLLER:", value)
        return float(value)


class GetCurrentSccmRrgBhControllerEffect(ManyDeviceControllerEffect):
    def _on_get_value(self, value):
        self._controller.current_sccms[self._controller._last_thread_command.kwargs['arg1']] = value

    def _call_function(self, value):
        return float(value)
