import random
from time import sleep

from ..commands import BaseCommand
from ..devices import CurrentSourceDevice
from ...conf import settings

from .base import AbstractController
from ...system_effects import (
    GetCurrentControllerAction,
    GetVoltageControllerAction,
    GetPowerControllerAction,
)

LOCAL_MODE = settings.LOCAL_MODE

MAX_CURRENT = 132.0
MAX_SET_CURRENT = 120.0  # MAX_CURRENT
CLEAR_COMMAND = "*CLS"
REMOTE_COMMAND = f"SYST:REM"
OUTPUT_1_COMMAND = f"OUTP 1"
OUTPUT_0_COMMAND = f"OUTP 0"
GET_ERRORS_COMMAND = "SYST:ERR?"
GET_CURRENT_ACTUAL = "SOURce:CURRent?"  # 10-4-32
GET_CURRENT_MEASURE = "MEASure:CURRent?"  # ???
GET_VOLTAGE_ACTUAL = "SOURce:VOLTage?"  # 10-4-35
GET_VOLTAGE_MEASURE = "MEASure:VOLTage?"  # ???
SET_MAX_VOLTAGE_LIMIT = "SOUR:VOLT:PROT:LEV 13.75"  # 10-4-36 Max voltage limit
SET_ZERO_VOLTAGE_LIMIT = "SOUR:VOLT:PROT:LEV 0"  # 10-4-36 Max voltage limit
# max_current_limit = "SOURce:CURRent:PROTection:LEVel 132"  # 10-4-43 Max current limit
SET_MAX_CURRENT_LIMIT = f"SOUR:CURR:PROT:LEV {int(MAX_CURRENT)}"  # 10-4-43 Max current limit
SET_ZERO_CURRENT_LIMIT = "SOUR:CURR:PROT:LEV 0"  # 10-4-43 Max current limit
# max_voltage_actual = "SOURce:VOLTage 13.12"  # 10-4-34 Voltage limit for actual value
SET_VOLTAGE_ACTUAL = "SOUR:VOLT 13.12"  # 10-4-34 Voltage limit for actual value
SET_ZERO_VOLTAGE_ACTUAL = "SOUR:VOLT 0"  # 10-4-34 Voltage limit for actual value
# max_current_actual = "SOURce:CURRent 1.0"  # 10-4-40 Current limit for actual value
SET_CURRENT_ACTUAL = "SOUR:CURR"  # 10-4-40 Current limit for actual value # + " 1.0"
SET_ZERO_CURRENT_ACTUAL = "SOUR:CURR 0"  # 10-4-40 Current limit for actual value

SLEEP_TIME = 0.05

current_label = 'Текущий ток (А)'
voltage_label = 'Текущее напряжение'
resistance_label = 'Текущее сопротивление'


class CurrentSourceController(AbstractController):
    device_class = CurrentSourceDevice
    code = 'current_source'
    logs_parameters = [current_label, voltage_label, resistance_label]

    def __init__(self,
                 # on_change_voltage=None,
                 # on_change_current=None,
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

        # self.target_voltage_value = 0.0
        self.target_current_value = 0.0

        self.loop_delay = 0.05

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
        self._exec_command(BaseCommand(command=CLEAR_COMMAND))
        print("|> Current source exec 1 command...")
        self._exec_command(BaseCommand(command=REMOTE_COMMAND))
        print("|> Current source exec 2 command...")
        # self._exec_command(BaseCommand(command=OUTPUT_1_COMMAND))
        # print("|> Current source exec 3 command...")
        # sleep(self.loop_delay)
        self._exec_command(BaseCommand(command=GET_ERRORS_COMMAND, ))
        print("|> Current source exec 3 command...")
        sleep(self.loop_delay * 2)
        read_value = self.read().strip()  # **self._CHECK_ERRORS_COMMAND_OBJ.kwargs
        print("Current source read value::", read_value)
        assert (read_value.lower() == "0 no error" or LOCAL_MODE)
        print("Current source >>> DONE!")

    def _thread_setup_additional(self, **kwargs):
        self.add_command(BaseCommand(command=CLEAR_COMMAND))
        self.add_command(BaseCommand(command=REMOTE_COMMAND))
        self.add_command(self.get_power_on_command())
        self.add_command(BaseCommand(command=SET_MAX_VOLTAGE_LIMIT))
        self.add_command(BaseCommand(command=SET_MAX_CURRENT_LIMIT))
        self.add_command(BaseCommand(command=SET_VOLTAGE_ACTUAL))

        # Repeat commands for updating values
        self.add_command(BaseCommand(
            # command=GET_CURRENT_ACTUAL,
            command=GET_CURRENT_MEASURE,
            repeat=True,
            with_answer=True,
            on_answer=self.actual_current_effect,
        ))
        self.add_command(BaseCommand(
            # command=GET_VOLTAGE_ACTUAL,
            command=GET_VOLTAGE_MEASURE,
            repeat=True,
            with_answer=True,
            on_answer=self.actual_voltage_effect,
        ))
        self._create_base_commands()

    def get_power_on_command(self):
        return BaseCommand(
            command=OUTPUT_1_COMMAND,
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
            command=OUTPUT_0_COMMAND,
            on_completed=self._on_turn_off_power,
        )

    def _on_turn_off_power(self):
        self.is_power_effect(False)

    def _create_base_commands(self):
        self._CHECK_ERRORS_COMMAND_OBJ = BaseCommand(
            command=GET_ERRORS_COMMAND,
            with_answer=True,
            on_answer=self._process_error_command
        )
        self._CLEAR_ERRORS_COMMAND_OBJ = BaseCommand(command=CLEAR_COMMAND)

    def _create_set_current_command_obj(self, value):
        return BaseCommand(
            command=SET_CURRENT_ACTUAL,
            value=value,
            with_answer=False,
        )

    def _on_thread_error(self, exception: Exception):
        super()._on_thread_error(Exception(f"Ошибка источника тока: {str(exception)}"))

    def _process_error_command(self, answer):
        if (not LOCAL_MODE) and answer and answer.lower() != "0 no error":
            self._on_thread_error(Exception(answer))
            self._add_command_force(self._CLEAR_ERRORS_COMMAND_OBJ)

    def _is_error_check_command(self, command: BaseCommand = None):
        if command is None:
            return True
        return command.kwargs.get("command", "") in [GET_ERRORS_COMMAND, CLEAR_COMMAND]

    def _run_thread_command(self, command: BaseCommand):
        if not self._is_error_check_command(command):
            self._add_command_force(self._CHECK_ERRORS_COMMAND_OBJ)
        return super()._run_thread_command(command)

    def _get_last_commands_to_exit(self):
        return [
            self._CLEAR_ERRORS_COMMAND_OBJ,
            BaseCommand(command=SET_ZERO_CURRENT_ACTUAL),
            BaseCommand(command=SET_ZERO_VOLTAGE_ACTUAL),
            self.get_power_off_command(),
        ]

    # def destructor(self):
    #     super().destructor()
    #     print("|> Current source destructor")
    #     # runc_commands   below
    #     # # self.exec_command(command=SET_ZERO_CURRENT_ACTUAL)
    #     # # sleep(SLEEP_TIME)
    #     # self.exec_command(command=SET_ZERO_CURRENT_ACTUAL)
    #     # sleep(SLEEP_TIME)
    #     # self.exec_command(command=SET_ZERO_VOLTAGE_ACTUAL)
    #     # sleep(SLEEP_TIME)
    #     # self.exec_command(command=OUTPUT_0_COMMAND)

    @AbstractController.device_command()
    def exec_command(self, command=None, value=None):
        answer = self.device.exec_command(command=command, value=value)
        sleep(0.05)
        errors = self.device.exec_command(command=GET_ERRORS_COMMAND)
        # print("|> CUR S:", answer, errors)
        if errors and errors.lower() != "0 no error":
            sleep(0.05)
            self.device.exec_command(command=CLEAR_COMMAND)
            raise Exception(errors)
        return answer

    def get_current_value(self):
        return self.current_value

    def get_voltage_value(self):
        return self.voltage_value

    @AbstractController.thread_command
    def _on_get_current_value(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = float(value)
        self.current_value = value

    @AbstractController.thread_command
    def _on_get_voltage_value(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = float(value)
        self.voltage_value = value
        # if self.on_change_voltage is not None:
        #     self.on_change_voltage(value)
        # return self.exec_command(command=GET_CURRENT_ACTUAL)

    @AbstractController.thread_command
    def set_target_current(self, value):
        value = float(value)
        value = round(max(0.0, min(value, MAX_SET_CURRENT)), 2)
        command = self._create_set_current_command_obj(value)
        self.target_current_value = value
        # print("Set value current:", self.target_current_value)
        self.add_command(command)
        return value

    def update_resistance(self, *args, **kwargs):
        if self.current_value <= 0.1:
            self.resistance_value = 0.0
        else:
            self.resistance_value = self.voltage_value / self.current_value
