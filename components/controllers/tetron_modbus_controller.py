import random
from time import sleep

from ..commands import BaseCommand
from ..devices import BaseModbusRtuDevice
from ...conf import settings

from .base import AbstractController
from ...system_effects import (
    GetCurrentControllerAction,
    GetVoltageControllerAction,
    GetPowerControllerAction,
)

LOCAL_MODE = settings.LOCAL_MODE

MAX_CURRENT = 166.0
MAX_VOLTAGE = 31.0

INIT_REMOTE_MODE = 0x0500

GET_CURRENT_ACTUAL = 0x0A07
GET_CURRENT_MEASURE = 0x0B02
GET_VOLTAGE_ACTUAL = 0x0A05
GET_VOLTAGE_MEASURE = 0x0B00
# SET_MAX_VOLTAGE_LIMIT = 0x0A05  # Max voltage limit # NOT USE THIS!
# SET_MAX_CURRENT_LIMIT = 0x0A03  # 166. # NOT USE THIS!
SET_VOLTAGE_ACTUAL = 0x0A05  # Voltage limit for actual value
SET_CURRENT_ACTUAL = 0x0A07

CONFIRM_SET_TARGET = 0x0A00
VOLTAGE_TARGET_REGISTER = 1
CURRENT_TARGET_REGISTER = 2
OUTPUT_ON_TARGET_REGISTER = 6
OUTPUT_OFF_TARGET_REGISTER = 7

SLEEP_TIME = 0.1

current_label = 'Текущий ток (А)'
voltage_label = 'Текущее напряжение'
resistance_label = 'Текущее сопротивление'


class TetronCurrentSourceController(AbstractController):
    device_class = BaseModbusRtuDevice
    code = 'current_source'
    logs_parameters = [current_label, voltage_label, resistance_label]

    def __init__(self,
                 **kwargs,
                 ):
        super().__init__(**kwargs)
        self._thread_using = True
        # self.on_change_voltage = on_change_voltage
        # self.on_change_current = on_change_current
        self.is_power = False
        self.voltage_value = 0.0
        self.current_value = 0.0
        self.resistance_value = 0.0

        self.target_current_value = 0.0

        self.loop_delay = SLEEP_TIME

        self.actual_current_effect = GetCurrentControllerAction(controller=self)
        self.actual_voltage_effect = GetVoltageControllerAction(controller=self)
        self.is_power_effect = GetPowerControllerAction(controller=self)

        self.actual_current_effect.connect(self.update_resistance)
        self.actual_voltage_effect.connect(self.update_resistance)

    def _get_log_values(self):
        return {
            current_label: self.current_value,
            voltage_label: self.voltage_value,
            resistance_label: self.resistance_value,
        }

    def _check_command(self, **kwargs):
        pass

    def _thread_setup_additional(self, **kwargs):
        self.add_command(BaseCommand(register=INIT_REMOTE_MODE, value=1, function_type='bit'))
        self.add_command(self.get_power_on_command())
        # self.add_command(BaseCommand(command=SET_MAX_VOLTAGE_LIMIT))
        # self.add_command(BaseCommand(command=SET_MAX_CURRENT_LIMIT))
        self.add_command(
            BaseCommand(register=SET_VOLTAGE_ACTUAL, value=MAX_VOLTAGE, function_type='float')
        )
        self.add_command(
            BaseCommand(
                register=CONFIRM_SET_TARGET,
                value=VOLTAGE_TARGET_REGISTER,
                function_type='register',
            ),
        )

        # Repeat commands for updating values
        self.add_command(BaseCommand(
            register=GET_CURRENT_MEASURE,
            function_type='float',
            repeat=True,
            # with_answer=True,
            immediate_answer=True,
            on_answer=self.actual_current_effect,
        ))
        self.add_command(BaseCommand(
            register=GET_VOLTAGE_MEASURE,
            function_type='float',
            repeat=True,
            # with_answer=True,
            immediate_answer=True,
            on_answer=self.actual_voltage_effect,
        ))

    def get_power_on_command(self):
        return BaseCommand(
            register=CONFIRM_SET_TARGET,
            value=OUTPUT_ON_TARGET_REGISTER,
            function_type='register',
            on_completed=self._on_turn_on_power,
        )

    def _on_turn_on_power(self):
        self.is_power_effect(True)

    def toggle_power(self):
        if self.is_power:
            self.add_command(self.get_power_off_command())
        else:
            self.add_command(self.get_power_on_command())

    def get_power_off_command(self):
        return BaseCommand(
            register=CONFIRM_SET_TARGET,
            value=OUTPUT_OFF_TARGET_REGISTER,
            function_type='register',
            on_completed=self._on_turn_off_power,
        )

    def _on_turn_off_power(self):
        self.is_power_effect(False)

    def _create_set_current_commands_obj(self, value):
        return [
            BaseCommand(
                register=SET_CURRENT_ACTUAL,
                value=value,
                function_type='float',
            ),
            BaseCommand(
                register=CONFIRM_SET_TARGET,
                value=CURRENT_TARGET_REGISTER,
                function_type='register',
            ),
        ]

    def _on_thread_error(self, exception: Exception):
        super()._on_thread_error(Exception(f"Ошибка источника тока Tetron: {str(exception)}, "
                                           f"Reg {self._last_thread_command.kwargs['register']}"))

    def _get_last_commands_to_exit(self):
        return self._create_set_current_commands_obj(0.) + [
            self.get_power_off_command(),
        ]

    # @AbstractController.device_command()
    # def exec_command(self, register=None, value=None):
    #     answer = self.device.exec_command(register=register, value=value)
    #     sleep(0.05)
    #     errors = self.device.exec_command(command=GET_ERRORS_COMMAND)
    #     # print("|> CUR S:", answer, errors)
    #     if errors and errors.lower() != "0 no error":
    #         sleep(0.05)
    #         self.device.exec_command(command=CLEAR_COMMAND)
    #         raise Exception(errors)
    #     return answer

    def get_current_value(self):
        return self.current_value

    def get_voltage_value(self):
        return self.voltage_value

    @AbstractController.thread_command
    def set_target_current(self, value):
        value = float(value)
        value = round(max(0.0, min(value, MAX_CURRENT)), 2)
        commands = self._create_set_current_commands_obj(value)
        self.target_current_value = value
        # print("Set value current:", self.target_current_value)
        for command in commands:
            self.add_command(command)
        return value

    def update_resistance(self, *args, **kwargs):
        if self.current_value <= 0.1:
            self.resistance_value = 0.0
        else:
            self.resistance_value = self.voltage_value / self.current_value
