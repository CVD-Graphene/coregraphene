import random
import time

from ...conf import settings

from .base import AbstractController
from ..commands import BaseCommand
from ..devices import BhRrgDevice
from ...system_effects import GetCurrentSccmRrgBhControllerEffect

LOCAL_MODE = settings.LOCAL_MODE

RRG_READ_VALUE = "MFC_READ"
RRG_WRITE_VALUE = "MFC_WRITE"

sccm_label = 'РРГ sccm [BH] '


class BhRrgController(AbstractController):
    device_class = BhRrgDevice
    code = 'rrg_bh'

    # logs_parameters = [sccm_label, ]

    def __init__(self, *args, get_potential_port=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._rrgs_config = kwargs.get('rrg_config')
        self.port = kwargs.get("port", None)
        self._get_potential_port = get_potential_port

        self.loop_delay = 0.2
        self._thread_using = True
        self.target_sccms = [0.0 for _ in self._rrgs_config]
        self.current_sccms = [0.0 for _ in self._rrgs_config]

        self.get_current_flow = GetCurrentSccmRrgBhControllerEffect(controller=self)

    def _reinitialize_communication(self):
        try:
            if self._get_potential_port is not None:
                new_port = self._get_potential_port(self.port, self.code)
                self.port = new_port
                self.device.update_communication(port=new_port)
        except Exception as e:
            print(f"|<<< REINITIALIZE {self.code} COMMUNICATION ERR:", e)

    def _set_logs_parameters_array(self):
        arr = []
        for rrg_config in self._rrgs_config:
            arr.append(sccm_label + rrg_config["NAME"])
        return arr

    def _on_simple_answer(self, value):
        print('|> BH ANSWER VALUE:', value)

    def _get_log_values(self):
        values = dict()
        for i, sccm in enumerate(self.current_sccms):
            values[self.logs_parameters[i]] = sccm
        return values

    def get_max_sccm_device(self, device_num=None):
        if device_num is None:
            return settings.MAX_DEFAULT_SCCM_VALUE
        return self._rrgs_config[device_num].get("MAX_SCCM", settings.MAX_DEFAULT_SCCM_VALUE)

    def _thread_setup_additional(self, **kwargs):
        for i in range(len(self._rrgs_config)):
            self.add_command(BaseCommand(
                repeat=True,
                command=RRG_READ_VALUE,
                arg1=i,
                with_answer=True,
                on_answer=self.get_current_flow,
            ))

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
            command=RRG_WRITE_VALUE,
            arg1=device_num,
            arg2=sccm,
            on_answer=self._on_simple_answer,
        ))

        # print("NEW SCCM:", sccm, "| MAX:", max_sccm)
        return sccm

    @AbstractController.device_command()
    def full_open(self, device_num):
        max_sccm = self.get_max_sccm_device(device_num=device_num)
        return self.set_target_sccm(max_sccm, device_num)

    @AbstractController.device_command()
    def full_close(self, device_num):
        return self.set_target_sccm(0, device_num)
