from ...system_effects import ManyDeviceControllerEffect, ControllerEffect
from coregraphene.conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class GetCurrentStateBackPressureValveControllerAction(ControllerEffect):

    def _on_get_value(self, value):
        self._controller.state = value

    def _call_function(self, value):
        return value


class GetPressureBackPressureValveControllerAction(ControllerEffect):
    def _on_get_value(self, value):
        self._controller.current_pressure = value

    def _call_function(self, value):
        return float(value)


class GetTargetPressureBackPressureValveControllerAction(ControllerEffect):
    def _on_get_value(self, value):
        self._controller.target_pressure = value

    def _call_function(self, value):
        return float(value)


class GetTargetOpenPercentBackPressureValveControllerAction(ControllerEffect):
    def _on_get_value(self, value):
        self._controller.target_open_percent = value

    def _call_function(self, value):
        return float(value)


class GetCurrentSccmRrgAdcControllerEffect(ManyDeviceControllerEffect):

    def _on_get_value(self, value):
        # print("CALL FUNC CURRENT FLOW CONTROLLER 2:", value)
        self._controller.current_sccms[self._controller._last_thread_command.device_num] = value

    def _call_function(self, value):
        return float(value)
