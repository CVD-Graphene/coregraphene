import random

from .base import AbstractController, AbstractControllerManyDevices
from ..commands import BaseCommand
from ..devices import RrgModbusDevice
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE

CLOSE = 1
OPEN = 0

OPEN_RRG_FLAGS = 0b0  # 0b1100
CLOSE_RRG_FLAGS = 0b1000
REGISTER_STATE_FLAGS_1 = 2
REGISTER_SET_FLOW = 4
REGISTER_GET_FLOW = REGISTER_SET_FLOW if LOCAL_MODE else 5


class SeveralRrgModbusController(AbstractControllerManyDevices):
    def __init__(self, config, **kwargs):
        super().__init__()

        self._thread_using = True

        self.devices = []
        for rrg_config in config:
            rrg = RrgModbusDevice(
                instrument_number=rrg_config['INSTRUMENT_NUMBER'],
                **kwargs
            )
            self.devices.append(rrg)

        self.devices_amount = len(self.devices)
        self.loop_delay = 0.1

        self.target_sccms = [0.0 for _ in self.devices]
        self.current_sccms = [0.0 for _ in self.devices]

    def _thread_setup_additional(self, **kwargs):
        for i in range(self.devices_amount):
            self.add_command(BaseCommand(
                register=REGISTER_STATE_FLAGS_1, value=CLOSE_RRG_FLAGS,
                functioncode=6,
                device_num=i,
            ))
            self.add_command(BaseCommand(
                register=REGISTER_SET_FLOW, value=0.0,
                functioncode=6,
                device_num=i,
            ))
            self.add_command(BaseCommand(
                register=REGISTER_GET_FLOW,
                device_num=i,
                repeat=True,
                immediate_answer=True,
                on_answer=self._on_get_current_flow,
            ))

    def _get_last_commands_to_exit(self):
        commands = []
        for i in range(self.devices_amount):
            commands += [
                BaseCommand(
                    register=REGISTER_SET_FLOW, value=0.0, device_num=i,
                    functioncode=6,
                ),
                BaseCommand(
                    register=REGISTER_STATE_FLAGS_1, value=CLOSE_RRG_FLAGS, device_num=i,
                    functioncode=6,
                ),
            ]
        return commands

    @AbstractController.device_command()
    def set_target_sccm(self, sccm: float, device_num):
        sccm = float(sccm)
        sccm = min(200.0, max(0.0, sccm))
        assert 0.0 <= sccm <= 200.0
        self.target_sccms[device_num] = sccm
        target_flow = sccm / 2.0 * 100

        if target_flow <= 0.001:  # TO CLOSE
            self.add_command(BaseCommand(
                register=REGISTER_SET_FLOW, value=0.0,
                functioncode=6,
                device_num=device_num,
            ))
            self.add_command(BaseCommand(
                register=REGISTER_STATE_FLAGS_1, value=CLOSE_RRG_FLAGS,
                functioncode=6,
                device_num=device_num,
            ))
        else:
            """
            1. Set flow to target value (= sccm / 2)
            2. Open rrg
            """
            self.add_command(BaseCommand(
                register=REGISTER_SET_FLOW, value=target_flow,
                functioncode=6,
                device_num=device_num,
            ))
            self.add_command(BaseCommand(
                register=REGISTER_STATE_FLAGS_1, value=OPEN_RRG_FLAGS,
                functioncode=6,
                device_num=device_num,
            ))

        return sccm

    @AbstractController.thread_command
    def _on_get_current_flow(self, value):
        if LOCAL_MODE:
            value = random.random() * 100 * 100
        value = float(value) / 100 * 2.0
        # print(f"CURRENT SCCM [{self._last_thread_command.device_num}]: {value}")
        self.current_sccms[self._last_thread_command.device_num] = value

    @AbstractController.device_command()
    def get_current_sccm(self, device_num):
        if LOCAL_MODE:
            self.current_sccms[device_num] = random.random() * 200
        return self.current_sccms[device_num]


class RrgModbusController(AbstractController):
    def __init__(self, **kwargs):
        super().__init__()
        self.device = RrgModbusDevice(
            **kwargs
        )
        self.is_open = False
        self.target_sccm = 0.0
        self.current_sccm = 0.0

    def _check_command(self, **kwargs):
        states = self.read(register=REGISTER_STATE_FLAGS_1)
        print("::: RRG STATE FLAGS:", states)
        current_flow = self.read(register=REGISTER_GET_FLOW)
        print("::: RRG CURRENT FLOW:", current_flow)
        assert current_flow >= 0.0

    @AbstractController.device_command()
    def set_target_sccm(self, sccm: float = 0.):
        sccm = min(200.0, max(0.0, sccm))
        assert 0.0 <= sccm <= 200.0
        self.target_sccm = sccm
        target_flow = sccm / 2.0

        if self.target_sccm <= 0.00001:  # TO CLOSE
            self.exec_command(register=REGISTER_SET_FLOW, value=0, functioncode=6,)
            self.exec_command(register=REGISTER_STATE_FLAGS_1, value=CLOSE_RRG_FLAGS, functioncode=6,)
            is_open = False
        else:
            """
            1. Set flow to target value (= sccm / 2)
            2. Open rrg
            """
            self.exec_command(register=REGISTER_SET_FLOW, value=target_flow, functioncode=6,)
            self.exec_command(register=REGISTER_STATE_FLAGS_1, value=OPEN_RRG_FLAGS, functioncode=6,)
            is_open = True

        self.is_open = is_open
        return self.is_open

    @AbstractController.device_command()
    def get_current_sccm(self):
        current_flow = self.read(register=REGISTER_GET_FLOW)
        self.current_sccm = current_flow * 2.0
        if LOCAL_MODE:
            self.current_sccm = random.random() * 200
        return self.current_sccm
