import random

from ...system_effects import GetCurrentFlowRrgControllerEffect
from .base import AbstractController, AbstractControllerManyDevices
from ..commands import BaseCommand
from ..devices import RrgModbusDevice
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE

OPEN_RRG_FLAGS = 6  # 0b0  # 0b1100 / 0b0
REGULATION_RRG_FLAGS = 19
CLOSE_RRG_FLAGS = 10  # 0b1000  # 8
REGISTER_STATE_FLAGS_1 = 2
REGISTER_STATE_FLAGS_2 = 3
REGISTER_SET_FLOW = 4
REGISTER_GET_FLOW = REGISTER_SET_FLOW if LOCAL_MODE else 5


class SeveralRrgModbusController(AbstractControllerManyDevices):
    code = 'rrg'

    def __init__(self, config, get_potential_port=None, port=None, **kwargs):
        super().__init__()

        self.port = port
        self._get_potential_port = get_potential_port
        self._thread_using = True
        self._rrgs_config = config

        self.devices = []
        for rrg_config in config:
            rrg = RrgModbusDevice(
                instrument_number=rrg_config['INSTRUMENT_NUMBER'],
                timeout=0.2,
                port=self.port,
                **kwargs
            )
            self.devices.append(rrg)

        self.devices_amount = len(self.devices)
        self.loop_delay = 0.4

        self.target_sccms = [0.0 for _ in self.devices]
        self.current_sccms = [0.0 for _ in self.devices]

        self.get_current_flow = GetCurrentFlowRrgControllerEffect(controller=self)

    def _reinitialize_communication(self):
        try:
            if self._get_potential_port is not None:
                new_port = self._get_potential_port(self.port, self.code)
                self.port = new_port
                for i, device in enumerate(self.devices):
                    print(f"|> UPDATE PORT {self.code} for device #{i + 1} {device}")
                    device.update_communication(port=new_port)
        except Exception as e:
            print(f"|<<< REINITIALIZE {self.code} COMMUNICATION ERR:", e)

    def get_max_sccm_device(self, device_num=None):
        if device_num is None:
            return settings.MAX_DEFAULT_SCCM_VALUE
        return self._rrgs_config[device_num].get("MAX_SCCM", settings.MAX_DEFAULT_SCCM_VALUE)

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
            # self.add_command(BaseCommand(
            #     register=REGISTER_STATE_FLAGS_2,
            #     device_num=i, #functioncode=3,
            #     repeat=True,
            #     immediate_answer=True,
            #     on_answer=self._on_get_state_flags_2,
            # ))
            self.add_command(BaseCommand(
                register=REGISTER_GET_FLOW,
                device_num=i,
                repeat=True,
                immediate_answer=True,
                # on_answer=self._on_get_current_flow,
                on_answer=self.get_current_flow,
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
        max_sccm = self.get_max_sccm_device(device_num=device_num)
        sccm = min(max_sccm, max(0.0, sccm))
        assert 0.0 <= sccm <= max_sccm

        self.target_sccms[device_num] = sccm
        target_flow = sccm / max_sccm * 100 * 100

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
                register=REGISTER_STATE_FLAGS_1, value=REGULATION_RRG_FLAGS,
                functioncode=6,
                device_num=device_num,
            ))

        # print("NEW SCCM:", sccm, "| MAX:", max_sccm)
        return sccm

    @AbstractController.device_command()
    def full_open(self, device_num):
        self.add_command(BaseCommand(
            register=REGISTER_STATE_FLAGS_1, value=OPEN_RRG_FLAGS,
            functioncode=6,
            device_num=device_num,
        ))

        return self.get_max_sccm_device(device_num=device_num)

    @AbstractController.device_command()
    def full_close(self, device_num):
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

        return 0

    # @AbstractController.thread_command
    # def _on_get_current_flow(self, value):
    #     if LOCAL_MODE:
    #         value = random.random() * 100 * 100
    #     value = round(float(value) / 100 * 2.0, 1)
    #     print(f"CURRENT SCCM [{self._last_thread_command.device_num}]: {value}")
    #     self.current_sccms[self._last_thread_command.device_num] = value
    #     self.get_current_flow(value)

    # @AbstractController.thread_command
    # def _on_get_state_flags_2(self, value):
    #     if LOCAL_MODE:
    #         value = int(random.random() * 100)
    #     print(f"STATE FLAGS 2 [{self._last_thread_command.device_num}]:", "{0:b}".format(value))

    @AbstractController.thread_command
    def _on_get_target_flow(self, value):
        if LOCAL_MODE:
            value = random.random() * 100 * 100
        value = float(value) #/ 100 * 2.0
        print(f"TARGET SCCM [{self._last_thread_command.device_num}]: {value}")
        # self.current_sccms[self._last_thread_command.device_num] = value

    @AbstractController.device_command()
    def get_current_sccm(self, device_num):
        if LOCAL_MODE:
            self.current_sccms[device_num] = random.random() * settings.MAX_DEFAULT_SCCM_VALUE
        return self.current_sccms[device_num]


class RrgModbusController(AbstractController):
    def __init__(self, max_sccm=None, **kwargs):
        super().__init__()
        self.device = RrgModbusDevice(
            **kwargs
        )
        self.is_open = False
        self.target_sccm = 0.0
        self.current_sccm = 0.0

        self.max_sccm = max_sccm or settings.MAX_DEFAULT_SCCM_VALUE

    def _check_command(self, **kwargs):
        states = self.read(register=REGISTER_STATE_FLAGS_1)
        # print("::: RRG STATE FLAGS:", states)
        current_flow = self.read(register=REGISTER_GET_FLOW)
        # print("::: RRG CURRENT FLOW:", current_flow)
        assert current_flow >= 0.0

    @AbstractController.device_command()
    def set_target_sccm(self, sccm: float = 0.):
        sccm = min(self.max_sccm, max(0.0, sccm))
        assert 0.0 <= sccm <= self.max_sccm
        self.target_sccm = sccm
        target_flow = sccm / self.max_sccm * 100 * 100

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
            self.exec_command(register=REGISTER_STATE_FLAGS_1, value=REGULATION_RRG_FLAGS, functioncode=6,)
            is_open = True

        self.is_open = is_open
        return self.is_open

    @AbstractController.device_command()
    def get_current_sccm(self):
        current_flow = self.read(register=REGISTER_GET_FLOW)
        self.current_sccm = current_flow / 100.0 * self.max_sccm
        if LOCAL_MODE:
            self.current_sccm = random.random() * self.max_sccm
        return self.current_sccm
