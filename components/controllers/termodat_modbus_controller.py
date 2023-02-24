import random

from .base import AbstractController, AbstractControllerManyDevices
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
REGISTER_SPEED_SET = 355

MAX_TEMPERATURE = 100.0


class SeveralTermodatModbusController(AbstractControllerManyDevices):
    def __init__(self, config=None, **kwargs):
        super().__init__()

        self.devices = []
        for termodat_config in config:
            termodat = TermodatModbusDevice(
                instrument_number=termodat_config['INSTRUMENT_NUMBER'],
                **kwargs
            )
            self.devices.append(termodat)

        self.devices_amount = len(self.devices)
        self.loop_delay = 0.1

        self._thread_using = True
        self.state = OFF

        self.target_temperatures = [0.0 for _ in self.devices]
        self.current_temperatures = [0.0 for _ in self.devices]
        self.speeds = [0.0 for _ in self.devices]

    def _thread_setup_additional(self, **kwargs):
        for i in range(self.devices_amount):
            self.add_command(BaseCommand(
                register=REGISTER_ON_OFF, value=OFF, precision=PRECISION,
                device_num=i,
            ))
            self.add_command(BaseCommand(
                register=REGISTER_SPEED_SET,
                value=settings.TERMODAT_DEFAULT_SPEED,
                functioncode=6,
                precision=PRECISION,
                device_num=i,
            ))

            # Repeat commands for updating values
            self.add_command(BaseCommand(
                register=REGISTER_CURRENT_TEMPERATURE_GET,
                precision=PRECISION,
                device_num=i,
                repeat=True,
                immediate_answer=True,
                on_answer=self._on_get_current_temperature,
            ))
            self.add_command(BaseCommand(
                register=REGISTER_TARGET_TEMPERATURE_GET,
                precision=PRECISION,
                device_num=i,
                repeat=True,
                immediate_answer=True,
                on_answer=self._on_get_target_temperature,
            ))

    def _get_last_commands_to_exit(self):
        commands = []
        for i in range(self.devices_amount):
            commands += [
                BaseCommand(
                    device_num=i,
                    register=REGISTER_ON_OFF, value=ON, precision=PRECISION,
                ),
                BaseCommand(
                    device_num=i,
                    register=REGISTER_TARGET_TEMPERATURE_SET, value=0.0,
                ),
                BaseCommand(
                    device_num=i,
                    register=REGISTER_ON_OFF, value=OFF, precision=PRECISION,
                ),
            ]
        return commands

    def _create_set_target_temperaturn_command_obj(self, temperature, device_num):
        return BaseCommand(
            register=REGISTER_TARGET_TEMPERATURE_SET,
            value=temperature,
            device_num=device_num,
        )

    @AbstractController.thread_command
    def turn_on_termodat_regulation(self, device_num):
        return self.set_is_active_regulation(True, device_num)

    @AbstractController.thread_command
    def turn_off_termodat_regulation(self, device_num):
        return self.set_is_active_regulation(False, device_num)

    @AbstractController.thread_command
    def turn_on_all_termodats_regulation(self):
        for device_num in range(self.devices_amount):
            self.turn_on_termodat_regulation(device_num)
        return True

    @AbstractController.thread_command
    def turn_off_all_termodats_regulation(self):
        for device_num in range(self.devices_amount):
            self.turn_off_termodat_regulation(device_num)
        return False

    @AbstractController.thread_command
    def set_temperature_and_speed_all_termodats(self, temperature, speed):
        # print("TS:::", temperature, speed, type(temperature), type(speed))
        temperature = float(temperature)
        speed = float(speed)
        # print("TS2:::", temperature, speed)
        for device_num in range(self.devices_amount):
            self.set_target_temperature(temperature, device_num)
            self.set_speed_regulation(speed, device_num)
        return [temperature, speed]

    @AbstractController.thread_command
    def set_temperature_all_termodats(self, temperature):
        temperature = float(temperature)
        for device_num in range(self.devices_amount):
            self.set_target_temperature(temperature, device_num)
        return temperature

    @AbstractController.thread_command
    def set_target_temperature(self, value, device_num):
        value = float(value)
        # value = min(value, MAX_TEMPERATURE)
        print("|> Set value [TARGET TEMP]:", value)
        command = self._create_set_target_temperaturn_command_obj(value, device_num)
        self.add_command(command)
        return value

    @AbstractController.thread_command
    def set_is_active_regulation(self, is_active: bool, device_num):
        command = BaseCommand(
            device_num=device_num,
            register=REGISTER_ON_OFF,
            value=ON if is_active else OFF,
            precision=PRECISION,
        )
        self.add_command(command)
        return is_active

    @AbstractController.thread_command
    def set_speed_regulation(self, speed: float, device_num):
        self.add_command(BaseCommand(
            register=REGISTER_SPEED_SET,
            functioncode=6,
            value=speed,
            precision=PRECISION,
            device_num=device_num,
        ))
        return speed

    @AbstractController.thread_command
    def _on_get_current_temperature(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = round(float(value), 1)
        self.current_temperatures[self._last_thread_command.device_num] = value
        # if self.on_change_current is not None:
        #     self.on_change_current(value)

    @AbstractController.thread_command
    def _on_get_target_temperature(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = round(float(value), 1)
        self.target_temperatures[self._last_thread_command.device_num] = value

    def get_target_temperature(self, device_num):
        return self.target_temperatures[device_num]

    def get_current_temperature(self, device_num):
        return self.current_temperatures[device_num]


class TermodatModbusController(AbstractController):
    def __init__(self, **kwargs):
        super().__init__()
        self.device = TermodatModbusDevice(
            **kwargs,
        )
        self.loop_delay = 0.5

        self._thread_using = True
        self.state = OFF
        self.target_temperature = 0.0
        self.current_temperature = 0.0
        self.speed = 0.0

    def _check_command(self, **kwargs):
        self.exec_command(register=REGISTER_ON_OFF, value=ON, precision=PRECISION,)
        current_temperature = self.read(
            register=REGISTER_CURRENT_TEMPERATURE_GET,
            precision=PRECISION,
        )
        self.exec_command(register=REGISTER_ON_OFF, value=OFF, precision=PRECISION,)
        print("TERMODAT current_temperature:", current_temperature)
        assert current_temperature >= 0.0

    def _thread_setup_additional(self, **kwargs):
        self.add_command(BaseCommand(
            register=REGISTER_ON_OFF, value=ON, precision=PRECISION,
        ))

        # Repeat commands for updating values
        self.add_command(BaseCommand(
            register=REGISTER_CURRENT_TEMPERATURE_GET,
            precision=PRECISION,
            repeat=True,
            immediate_answer=True,
            on_answer=self._on_get_current_temperature,
        ))
        self.add_command(BaseCommand(
            register=REGISTER_TARGET_TEMPERATURE_GET,
            precision=PRECISION,
            repeat=True,
            immediate_answer=True,
            on_answer=self._on_get_target_temperature,
        ))

    def _get_last_commands_to_exit(self):
        return [
            BaseCommand(register=REGISTER_TARGET_TEMPERATURE_SET, value=0.0),
            BaseCommand(register=REGISTER_ON_OFF, value=OFF, precision=PRECISION,),
        ]

    def _create_set_target_temperaturn_command_obj(self, temperature):
        return BaseCommand(
            register=REGISTER_TARGET_TEMPERATURE_SET,
            value=temperature,
        )

    @AbstractController.thread_command
    def set_target_temperature(self, value):
        value = float(value)
        # value = min(value, MAX_TEMPERATURE)
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
