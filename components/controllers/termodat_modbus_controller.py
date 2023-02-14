import random

from .base import AbstractController
from ..commands import BaseCommand
from ..devices import TermodatModbusDevice
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE

PRECISION = 1
REGISTER_ON_OFF = 384  # Register for on/off device
ON, OFF = 1, 0
REGISTER_CURRENT_TEMPERATURE_GET = 368
REGISTER_TARGET_TEMPERATURE_GET = 369  # 48 - too
REGISTER_TARGET_TEMPERATURE_SET = 371
REGISTER_SPEED_SET = 377

MAX_TEMPERATURE = 60.0


class TermodatModbusController(AbstractController):
    def __init__(self, **kwargs):
        super().__init__()
        self.device = TermodatModbusDevice(
            **kwargs,
        )

        self._thread_using = True
        self.state = OFF
        self.target_temperature = 0.0
        self.current_temperature = 0.0
        self.speed = 0.0

    def _check_command(self, **kwargs):
        self.exec_command(register=REGISTER_ON_OFF, value=ON)
        current_temperature = self.read(
            register=REGISTER_CURRENT_TEMPERATURE_GET)
        self.exec_command(register=REGISTER_ON_OFF, value=OFF)
        assert current_temperature >= 0.0

    def _thread_setup_additional(self, **kwargs):
        self.add_command(BaseCommand(
            register=REGISTER_ON_OFF, value=ON,
        ))

        # Repeat commands for updating values
        self.add_command(BaseCommand(
            register=REGISTER_CURRENT_TEMPERATURE_GET,
            repeat=True,
            immediate_answer=True,
            on_answer=self._on_get_current_temperature,
        ))
        self.add_command(BaseCommand(
            register=REGISTER_TARGET_TEMPERATURE_GET,
            repeat=True,
            immediate_answer=True,
            on_answer=self._on_get_target_temperature,
        ))

    def _get_last_commands_to_exit(self):
        return [
            BaseCommand(register=REGISTER_TARGET_TEMPERATURE_SET, value=0.0),
            BaseCommand(register=REGISTER_ON_OFF, value=OFF),
        ]

    def _create_set_target_temperaturn_command_obj(self, temperature):
        return BaseCommand(
            register=REGISTER_TARGET_TEMPERATURE_SET,
            value=temperature,
        )

    @AbstractController.thread_command
    def set_target_temperature(self, value):
        value = float(value)
        value = min(value, MAX_TEMPERATURE)
        command = self._create_set_target_temperaturn_command_obj(value)
        print("|> Set value [TARGET TEMP]:", value)
        self.add_command(command)
        return value

    @AbstractController.thread_command
    def _on_get_current_temperature(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = float(value)
        self.current_temperature = value
        # if self.on_change_current is not None:
        #     self.on_change_current(value)

    @AbstractController.thread_command
    def _on_get_target_temperature(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = float(value)
        self.target_temperature = value

    def get_target_temperature(self):
        return self.target_temperature

    def get_current_temperature(self):
        return self.current_temperature
