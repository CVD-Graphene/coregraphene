import random
import time

from ...conf import settings

from .base import AbstractController
from ..commands import BaseCommand
from ..devices import PyrometerTemperatureDevice
from ...system_actions import GetCurrentTemperaturePyrometerControllerAction

LOCAL_MODE = settings.LOCAL_MODE


class PyrometerTemperatureController(AbstractController):
    device_class = PyrometerTemperatureDevice
    code = 'pyrometer'

    def __init__(self, *args, get_potential_port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.port = kwargs.get("port", None)
        self._get_potential_port = get_potential_port

        self.temperature_value = 0.0
        self.loop_delay = 0.2
        self._thread_using = True

        self.get_temperature_action = GetCurrentTemperaturePyrometerControllerAction(controller=self)

    def _reinitialize_communication(self):
        try:
            if self._get_potential_port is not None:
                new_port = self._get_potential_port(self.port, self.code)
                self.port = new_port
                self.device.update_communication(port=new_port)
        except Exception as e:
            print(f"|<<< REINITIALIZE {self.code} COMMUNICATION ERR:", e)

    def _thread_setup_additional(self, **kwargs):
        self.add_command(BaseCommand(
            command="\x0201RD000001\x031B\0",
            repeat=True,
            # immediate_answer=True,
            with_answer=True,  # NOT IMMEDIATE ANSWER because we need to send firstly
            # on_answer=self._on_get_temperature_value,
            on_answer=self.get_temperature_action,
        ))

    @AbstractController.thread_command
    def _on_get_temperature_value(self, value):
        if LOCAL_MODE:
            value = round(random.random() * 1000, 1)
        value = float(value)
        self.temperature_value = value

    def _check_command(self, **kwargs):
        value = -1
        assert value >= 0.0
