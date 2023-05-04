import time

from .base import AbstractController
from ..commands import BaseCommand
from ..devices import BackPressureValveDevice
from ...conf import settings
from ...constants.components import BACK_PRESSURE_VALVE_STATE, BACK_PRESSURE_VALVE_CONSTANTS
from ...system_effects import (
    GetCurrentStateBackPressureValveControllerAction,
    GetPressureBackPressureValveControllerAction,
    GetTargetPressureBackPressureValveControllerAction,
)
from ...system_effects.controllers.back_pressure_valve import GetTargetOpenPercentBackPressureValveControllerAction

LOCAL_MODE = settings.LOCAL_MODE
FULL_OPEN_BORDER = 99.7
FULL_CLOSE_BORDER = 0.3


class BackPressureValveController(AbstractController):
    code = 'throttle'
    device_class = BackPressureValveDevice

    def __init__(self, get_potential_port=None, port=None, **kwargs):
        super().__init__(port=port, **kwargs)

        self.port = port
        self._get_potential_port = get_potential_port

        self.loop_delay = 0.2
        self._thread_using = True

        self.state = BACK_PRESSURE_VALVE_STATE.CLOSE
        self.current_pressure = 0.0
        self.target_pressure = 0.0
        self.target_open_percent = 0.0

        self.get_state_action = GetCurrentStateBackPressureValveControllerAction(controller=self)
        self.get_current_pressure_action = GetPressureBackPressureValveControllerAction(controller=self)
        self.get_target_pressure_action = GetTargetPressureBackPressureValveControllerAction(controller=self)
        self.get_target_open_percent_action = GetTargetOpenPercentBackPressureValveControllerAction(controller=self)

    def _check_command(self, **kwargs):
        self._exec_command(BaseCommand(command=BACK_PRESSURE_VALVE_CONSTANTS.READ_PRESSURE,))
        time.sleep(self.loop_delay * 2)
        read_value = str(self.read())
        print("Throttle get value::", read_value)
        assert read_value >= 0.0
        print("Throttle >>> DONE!")

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
            command=BACK_PRESSURE_VALVE_CONSTANTS.READ_PRESSURE,
            repeat=True,
            with_answer=True,
            on_answer=self.get_current_pressure_action,
        ))
        self.add_command(self._create_read_target_pressure_command_obj())

    def _get_last_commands_to_exit(self):
        return [
            BaseCommand(
                command=BACK_PRESSURE_VALVE_CONSTANTS.WRITE_TARGET_PRESSURE,
                value=BACK_PRESSURE_VALVE_CONSTANTS.MIN_PRESSURE_BORDER,
            ),
            BaseCommand(
                command=BACK_PRESSURE_VALVE_CONSTANTS.FULL_CLOSE,
            ),
        ]

    @AbstractController.thread_command
    def on_change_state(self):
        # print("current STATE throttle:", self.state)
        if self.state == BACK_PRESSURE_VALVE_STATE.OPEN:
            return self.on_full_close()
        elif self.state == BACK_PRESSURE_VALVE_STATE.CLOSE:
            return self.on_full_open()
        elif self.state == BACK_PRESSURE_VALVE_STATE.REGULATION:
            return self.on_full_close()
        return BACK_PRESSURE_VALVE_STATE.WAITING

    def _create_read_target_pressure_command_obj(self):
        return BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.READ_TARGET_PRESSURE,
            with_answer=True,
            on_answer=self.get_target_pressure_action,
        )

    def _create_set_target_pressure_command_obj(self, pressure):
        return BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.WRITE_TARGET_PRESSURE,
            value=pressure,
        )

    def _create_set_target_percent_command_obj(self, percent):
        return BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.WRITE_TARGET_PERCENT,
            value=percent,
        )

    @AbstractController.thread_command
    def on_full_open(self):
        # print("On full open start!")
        self.get_target_open_percent_action(100.0)
        self.add_command(BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.FULL_OPEN,
        ))
        self.add_command(self._create_full_open_checker_command_obj())
        return self.get_state_action(BACK_PRESSURE_VALVE_STATE.WAITING)

    def _create_full_open_checker_command_obj(self):
        return BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.READ_VALVE_POSITION_PERCENT,
            with_answer=True,
            on_answer=self._on_full_open_checker,
        )

    def _on_full_open_checker(self, percent=0.1):
        # print("CURRENT PERCENT VALVE [on full open]:", percent)
        if percent < FULL_OPEN_BORDER:
            self.add_command(self._create_full_open_checker_command_obj())
        else:
            self.get_state_action(BACK_PRESSURE_VALVE_STATE.OPEN)

    @AbstractController.thread_command
    def on_full_close(self):
        self.get_target_open_percent_action(0.0)
        self.add_command(BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.FULL_CLOSE,
        ))
        self.add_command(self._create_full_close_checker_command_obj())
        return self.get_state_action(BACK_PRESSURE_VALVE_STATE.WAITING)

    def _create_full_close_checker_command_obj(self):
        return BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.READ_VALVE_POSITION_PERCENT,
            with_answer=True,
            on_answer=self._on_full_close_checker,
        )

    def _on_full_close_checker(self, percent=99.9):
        if percent > FULL_CLOSE_BORDER:
            self.add_command(self._create_full_close_checker_command_obj())
        else:
            self.get_state_action(BACK_PRESSURE_VALVE_STATE.CLOSE)

    @AbstractController.thread_command
    def turn_on_regulation(self, pressure):
        pressure = float(pressure)
        # print("Turn on regulation to", pressure)
        self.add_command(self._create_set_target_pressure_command_obj(pressure))
        self.add_command(BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.START_REGULATION,
            # with_answer=True,  # ON END, NOT ON ANSWER
            on_completed=self._on_turn_on_regulation,
        ))
        self.add_command(self._create_read_target_pressure_command_obj())
        self.get_state_action(BACK_PRESSURE_VALVE_STATE.WAITING)
        return pressure
        # self.state = BACK_PRESSURE_VALVE_STATE.WAITING
        # return self.state

    def _on_turn_on_regulation(self):
        # print("_on_turn_on_regulation!!!!!")
        return self.get_state_action(BACK_PRESSURE_VALVE_STATE.REGULATION)

    @AbstractController.thread_command
    def set_target_percent(self, percent):
        percent = float(percent)
        # print("Turn on keeping percent to", percent)
        self.add_command(self._create_set_target_percent_command_obj(percent))
        self.add_command(BaseCommand(
            command=BACK_PRESSURE_VALVE_CONSTANTS.KEEP_TARGET_PERCENT,
            on_completed=self._on_turn_on_keeping_percent,
        ))
        # self.add_command(self._create_read_target_pressure_command_obj())
        self.get_state_action(BACK_PRESSURE_VALVE_STATE.WAITING)
        return percent
        # self.state = BACK_PRESSURE_VALVE_STATE.WAITING
        # return self.state

    def _on_turn_on_keeping_percent(self):
        # print("_on_turn_on_keeping_percent!!!!!")
        return self.get_state_action(BACK_PRESSURE_VALVE_STATE.REGULATION)
