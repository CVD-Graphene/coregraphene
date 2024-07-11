from ...conf import settings

from .base import AbstractController
from ..commands import BaseCommand
from ..devices import PumpTC110Device
from ...system_effects import GetActualSpeedPumpTC110ControllerEffect

LOCAL_MODE = settings.LOCAL_MODE

ACTUAL_SPEED_COMMAND = "309"
SET_SPEED_COMMAND = "717"
ON_1_COMMAND = "010"
ON_2_COMMAND = "002"
OFF_1_COMMAND = "002"
OFF_2_COMMAND = "010"

speed_label = 'Текущие обороты, Hz'


class PumpTC110Controller(AbstractController):
    device_class = PumpTC110Device
    code = 'pump_tc110'

    logs_parameters = [speed_label, ]

    def __init__(self, *args, get_potential_port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.port = kwargs.get("port", None)
        self._get_potential_port = get_potential_port

        self.loop_delay = 0.2
        self._thread_using = True

        # PARAMS
        self.is_active = False
        self.target_speed = 0
        # self.current_speed = 0.0
        self.actual_speed = 0.0

        self.get_actual_speed_action = GetActualSpeedPumpTC110ControllerEffect(controller=self)

    def _reinitialize_communication(self):
        try:
            if self._get_potential_port is not None:
                new_port = self._get_potential_port(self.port, self.code)
                self.port = new_port
                self.device.update_communication(port=new_port)
        except Exception as e:
            print(f"|<<< REINITIALIZE {self.code} COMMUNICATION ERR:", e)

    def _on_simple_answer(self, value):
        pass
        # print('|> BH ANSWER VALUE:', value)

    def _get_log_values(self):
        values = dict()
        values[speed_label] = self.actual_speed
        return values

    def _thread_setup_additional(self, **kwargs):
        self.add_command(BaseCommand(
            repeat=True,
            command=ACTUAL_SPEED_COMMAND,
            with_answer=True,
            on_answer=self.get_actual_speed_action,
        ))

    def get_off_commands(self):
        return [
            BaseCommand(command=OFF_1_COMMAND),
            BaseCommand(command=OFF_2_COMMAND),
        ]

    def get_on_commands(self):
        return [
            BaseCommand(command=ON_1_COMMAND),
            BaseCommand(command=ON_2_COMMAND),
        ]

    def _get_last_commands_to_exit(self):
        commands_list = self.get_off_commands()
        return commands_list

    def _create_set_target_speed_command_obj(self, value):
        return BaseCommand(
            command=SET_SPEED_COMMAND,
            value=value,
            with_answer=True,
            on_answer=self.get_actual_speed_action,
        )

    @property
    def is_working(self):
        return self.is_active or (self.actual_speed > 0.0)

    @AbstractController.device_command()
    def set_target_speed_percent(self, percent: int):
        percent = int(percent)
        percent = min(100, max(20, percent))
        assert 20 <= percent <= 100

        self.target_speed = percent

        self.add_command(self._create_set_target_speed_command_obj(percent))

        return percent

    @AbstractController.device_command()
    def pump_turn_on(self):
        commands = self.get_on_commands()
        self.is_active = True
        for command in commands:
            self.add_command(command)
        return self.is_active

    @AbstractController.device_command()
    def pump_turn_off(self):
        commands = self.get_off_commands()
        self.is_active = False
        for command in commands:
            self.add_command(command)
        return self.is_active
