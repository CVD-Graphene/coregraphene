import random
import time

from ...conf import settings

from .base import AbstractController
from ..commands import BaseCommand
from ..devices import AccurateVakumetrDevice
from ...system_effects import GetCurrentPressureVakumetrControllerEffect

LOCAL_MODE = settings.LOCAL_MODE

parameter_label = 'Точный вакуметр'


class AccurateVakumetrController(AbstractController):
    device_class = AccurateVakumetrDevice
    code = 'vakumetr'

    logs_parameters = [parameter_label, ]

    def __init__(self, *args, get_potential_port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.port = kwargs.get("port", None)
        self._get_potential_port = get_potential_port

        # self.device = AccurateVakumetrDevice(port=self.port, **kwargs)
        self.vakumetr_value = 0.0
        self.loop_delay = 0.3

        self._thread_using = True
        self.actual_pressure_effect = GetCurrentPressureVakumetrControllerEffect(controller=self)

    def _reinitialize_communication(self):
        try:
            if self._get_potential_port is not None:
                new_port = self._get_potential_port(self.port, self.code)
                self.port = new_port
                self.device.update_communication(port=new_port)
        except Exception as e:
            print(f"|<<< REINITIALIZE {self.code} COMMUNICATION ERR:", e)

    def _get_log_values(self):
        return {parameter_label: self.vakumetr_value}

    def _thread_setup_additional(self, **kwargs):
        self.add_command(BaseCommand(
            command="DR",
            value="00",
            operation_code="2",
            repeat=False,
            with_answer=True,
            on_answer=self._on_reboot_answer,
        ))
        self.add_command(BaseCommand(
            command="MV",
            value="00",
            operation_code="0",
            repeat=True,
            with_answer=True,
            # on_answer=self._on_get_vakumetr_value,
            on_answer=self.actual_pressure_effect,
        ))

    @AbstractController.thread_command
    def _on_get_vakumetr_value(self, value):
        if LOCAL_MODE:
            value = round(random.random() * 100, 2)
        value = float(value)
        self.vakumetr_value = value
        # if self.on_change_voltage is not None:
        #     self.on_change_voltage(value)

    @AbstractController.thread_command
    def _on_reboot_answer(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = float(value)
        print("REBOOT ANSWER", value)

    def destructor(self):
        super().destructor()
        print("|> Accurate vakumetr destructor!")

    def _check_command(self, **kwargs):
        # self.device.exec_command(
        #     command="DR",
        #     value="00",
        #     operation_code="2",
        # )
        # time.sleep(1)
        # print(self.device.read(), "REBOOT READ")
        value = self.device.get_value_with_waiting()
        assert value >= 0.0
        print("Vakumetr >>> DONE!")

    def get_value(self):
        return self.device.get_value()
