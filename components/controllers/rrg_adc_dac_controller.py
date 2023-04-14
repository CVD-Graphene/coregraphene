import random

from ...system_actions import GetCurrentFlowRrgControllerAction, GetCurrentSccmRrgAdcControllerAction
from .base import AbstractController, AbstractControllerManyDevices
from ..commands import BaseCommand
from ..devices import RrgAdcDacDevice
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class SeveralRrgAdcDacController(AbstractControllerManyDevices):
    code = 'rrg'

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)

        self._thread_using = True
        self._rrgs_config = config

        self.devices = []
        for rrg_config in config:
            rrg = RrgAdcDacDevice(
                address=rrg_config['ADDRESS'],
                **kwargs,
            )
            self.devices.append(rrg)
            # break

        self.devices_amount = len(self.devices)
        self.loop_delay = 0.2

        self.target_sccms = [0.0 for _ in self.devices]
        self.current_sccms = [0.0 for _ in self.devices]

        self.get_current_flow = GetCurrentSccmRrgAdcControllerAction(controller=self)

    def get_max_sccm_device(self, device_num=None):
        if device_num is None:
            return settings.MAX_DEFAULT_SCCM_VALUE
        return self._rrgs_config[device_num].get("MAX_SCCM", settings.MAX_DEFAULT_SCCM_VALUE)

    def _thread_setup_additional(self, **kwargs):
        for i in range(self.devices_amount):
            self.add_command(BaseCommand(
                # register=REGISTER_GET_FLOW,
                device_num=i,
                repeat=True,
                immediate_answer=True,
                on_answer=self.get_current_flow,
            ))
            # break

    @AbstractController.device_command()
    def set_target_sccm(self, sccm: float, device_num):
        sccm = float(sccm)
        max_sccm = self.get_max_sccm_device(device_num=device_num)
        sccm = min(max_sccm, max(0.0, sccm))
        assert 0.0 <= sccm <= max_sccm

        self.target_sccms[device_num] = sccm
        # target_flow = sccm / max_sccm * 100 * 100
        # print("CREATE SCCM TARGET COMMAND")

        self.add_command(BaseCommand(
            value=sccm,
            device_num=device_num,
        ))

        # print("NEW SCCM:", sccm, "| MAX:", max_sccm)
        return sccm

    @AbstractController.device_command()
    def full_open(self, device_num):
        max_sccm = self.get_max_sccm_device(device_num=device_num)
        return self.set_target_sccm(max_sccm, device_num)
        # max_sccm = self.get_max_sccm_device(device_num=device_num)
        # self.target_sccms[device_num] = max_sccm
        # self.add_command(BaseCommand(
        #     value=max_sccm,
        #     device_num=device_num,
        # ))
        #
        # return max_sccm

    @AbstractController.device_command()
    def full_close(self, device_num):
        return self.set_target_sccm(0, device_num)
        # self.target_sccms[device_num] = 0
        # self.add_command(BaseCommand(
        #     value=0,
        #     device_num=device_num,
        # ))
        #
        # return 0
