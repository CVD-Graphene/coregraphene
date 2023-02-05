import random
from time import sleep

from ..commands import BaseCommand
from ..devices import CurrentSourceDevice
from ...conf import settings

from .base import AbstractController

LOCAL_MODE = settings.LOCAL_MODE

MAX_CURRENT = 132.0
MAX_SET_CURRENT = 1.0  # MAX_CURRENT
CLEAR_COMMAND = "*CLS"
REMOTE_COMMAND = f"SYST:REM"
OUTPUT_1_COMMAND = f"OUTP 1"
OUTPUT_0_COMMAND = f"OUTP 0"
GET_ERRORS_COMMAND = "SYST:ERR?"
GET_CURRENT_ACTUAL = "SOURce:CURRent?"  # 10-4-32
GET_VOLTAGE_ACTUAL = "SOURce:VOLTage?"  # 10-4-35
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


class CurrentSourceController(AbstractController):
    device_class = CurrentSourceDevice

    def __init__(self,
                 on_change_voltage=None,
                 on_change_current=None,
                 on_set_current=None,
                 ):
        super().__init__()
        self.on_change_voltage = on_change_voltage
        self.on_change_current = on_change_current
        self.on_set_current = on_set_current
        self.voltage_value = 0.0
        self.current_value = 0.0

    def setup(self):
        super().setup()
        # self.exec_command(command=CLEAR_COMMAND)
        # sleep(SLEEP_TIME)
        # self.exec_command(command=REMOTE_COMMAND)
        # sleep(SLEEP_TIME)
        # self.exec_command(command=OUTPUT_1_COMMAND)
        # sleep(SLEEP_TIME)
        # self.exec_command(command=SET_MAX_VOLTAGE_LIMIT)
        # sleep(SLEEP_TIME)
        # self.exec_command(command=SET_MAX_CURRENT_LIMIT)
        # sleep(SLEEP_TIME)
        # self.exec_command(command=SET_VOLTAGE_ACTUAL)

    def thread_setup(self, is_working, add_log, add_error, **kwargs):
        super().thread_setup(is_working, add_log, add_error)
        self.add_command(BaseCommand(command=CLEAR_COMMAND))
        self.add_command(BaseCommand(command=REMOTE_COMMAND))
        self.add_command(BaseCommand(command=OUTPUT_1_COMMAND))
        self.add_command(BaseCommand(command=SET_MAX_VOLTAGE_LIMIT))
        self.add_command(BaseCommand(command=SET_MAX_CURRENT_LIMIT))
        self.add_command(BaseCommand(command=SET_VOLTAGE_ACTUAL))

        # Repeat commands for updating values
        self.add_command(BaseCommand(
            command=GET_CURRENT_ACTUAL,
            repeat=True,
            with_answer=True,
            on_answer=self._on_get_current_value,
        ))
        self.add_command(BaseCommand(
            command=GET_VOLTAGE_ACTUAL,
            repeat=True,
            with_answer=True,
            on_answer=self._on_get_voltage_value,
        ))
        self._create_base_commands()

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
            # on_answer=self.on_set_current
        )

    def _on_thread_error(self, exception: Exception):
        super()._on_thread_error(Exception(f"Ошибка источника тока: {str(exception)}"))

    def _process_error_command(self, answer):
        if (not LOCAL_MODE) and answer and answer.lower() != "0 no error":
            self._on_thread_error(Exception(answer))
            self._add_command_force(self._CLEAR_ERRORS_COMMAND_OBJ)

    def _is_error_check_command(self, command: BaseCommand):
        if command is None:
            return True
        return command.command in [GET_ERRORS_COMMAND, CLEAR_COMMAND]

    def _run_thread_command(self, command: BaseCommand):
        if not self._is_error_check_command(command):
            self._add_command_force(self._CHECK_ERRORS_COMMAND_OBJ)
        return super()._run_thread_command(command)

    def _get_last_commands_to_exit(self):
        return [
            self._CLEAR_ERRORS_COMMAND_OBJ,
            BaseCommand(command=SET_ZERO_CURRENT_ACTUAL),
            BaseCommand(command=SET_ZERO_VOLTAGE_ACTUAL),
            BaseCommand(command=OUTPUT_0_COMMAND),
        ]

    def destructor(self):
        super().destructor()
        print("|> Current source destructor")
        # runc_commands   below
        # # self.exec_command(command=SET_ZERO_CURRENT_ACTUAL)
        # # sleep(SLEEP_TIME)
        # self.exec_command(command=SET_ZERO_CURRENT_ACTUAL)
        # sleep(SLEEP_TIME)
        # self.exec_command(command=SET_ZERO_VOLTAGE_ACTUAL)
        # sleep(SLEEP_TIME)
        # self.exec_command(command=OUTPUT_0_COMMAND)

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
        if self.on_change_current is not None:
            self.on_change_current(value)

    @AbstractController.thread_command
    def _on_get_voltage_value(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = float(value)
        self.voltage_value = value
        if self.on_change_voltage is not None:
            self.on_change_voltage(value)
        # return self.exec_command(command=GET_CURRENT_ACTUAL)

    @AbstractController.thread_command
    def set_current_value(self, value):
        value = float(value)
        value = min(value, MAX_SET_CURRENT)
        command = self._create_set_current_command_obj(value)
        print("Set value function:", value)
        self.add_command(command)
        # ans = self.exec_command(command=SET_CURRENT_ACTUAL, value=value)
        # raise Exception("Ошибка установки значения тока: ...")
        if self.on_set_current is not None:
            self.on_set_current(value)
        return value
