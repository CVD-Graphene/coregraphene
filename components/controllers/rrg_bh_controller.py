import random
import time

from ...conf import settings

from .base import AbstractController
from ..commands import BaseCommand
from ..devices import BhRrgDevice
from ...constants.components import BH_RRG_THROTTLE, BACK_PRESSURE_VALVE_STATE
from ...system_effects import GetCurrentSccmRrgBhControllerEffect

LOCAL_MODE = settings.LOCAL_MODE

sccm_label = 'РРГ sccm [BH] '
pressure_label = 'Давление дросселя'


class BhRrgController(AbstractController):
    device_class = BhRrgDevice
    code = 'rrg_bh'

    # logs_parameters = [sccm_label, ]

    def __init__(self, *args, get_potential_port=None, rrg_only=True, **kwargs):
        super().__init__(*args, **kwargs)

        self.rrg_only = rrg_only
        self._rrgs_config = kwargs.get('rrg_config')
        self.port = kwargs.get("port", None)
        self.max_rrg_voltage = kwargs.get("max_rrg_voltage", 5.0)
        self._get_potential_port = get_potential_port

        self.loop_delay = 0.2
        self._thread_using = True

        # RRG PARAMS
        self.target_sccms = [0.0 for _ in self._rrgs_config]
        self.current_sccms = [0.0 for _ in self._rrgs_config]

        self.get_current_flow = GetCurrentSccmRrgBhControllerEffect(controller=self)

        # THROTTLE PARAMS
        self.state = BACK_PRESSURE_VALVE_STATE.CLOSE
        self.throttle_current_pressure = 0.0
        self.throttle_target_pressure = 0.0
        self.throttle_target_open_percent = 0.0

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
        if not self.rrg_only:
            arr.append(pressure_label)
        return arr

    def _on_simple_answer(self, value):
        pass
        # print('|> BH ANSWER VALUE:', value)

    def _get_log_values(self):
        values = dict()
        for i, sccm in enumerate(self.current_sccms):
            values[self.logs_parameters[i]] = sccm
        if not self.rrg_only:
            values[pressure_label] = self.throttle_current_pressure
        return values

    def get_max_sccm_device(self, device_num=None):
        if device_num is None:
            return settings.MAX_DEFAULT_SCCM_VALUE
        return self._rrgs_config[device_num].get("MAX_SCCM", settings.MAX_DEFAULT_SCCM_VALUE)

    def _thread_setup_additional(self, **kwargs):
        for i in range(len(self._rrgs_config)):
            self.add_command(BaseCommand(
                repeat=True,
                command=BH_RRG_THROTTLE.RRG_READ_VALUE,
                arg1=i,
                device_num=i,
                with_answer=True,
                on_answer=self.get_current_flow,
            ))
        if not self.rrg_only:
            self.add_command(BaseCommand(
                command=BH_RRG_THROTTLE.THROTTLE_READ_PRESSURE,
                repeat=True,
                with_answer=True,
                on_answer=self.get_current_pressure_action,
            ))
            self.add_command(self._create_read_target_pressure_command_obj())

    def _get_last_commands_to_exit(self):
        commands_list = []
        if not self.rrg_only:
            commands_list += [
                BaseCommand(
                    command=BH_RRG_THROTTLE.THROTTLE_WRITE_TARGET_PRESSURE,
                    arg1=BH_RRG_THROTTLE.MIN_PRESSURE_BORDER,
                ),
                BaseCommand(
                    command=BH_RRG_THROTTLE.THROTTLE_FULL_CLOSE,
                ),
            ]
        return commands_list

    def _create_read_target_pressure_command_obj(self):
        return BaseCommand(
            command=BH_RRG_THROTTLE.THROTTLE_READ_TARGET_PRESSURE,
            with_answer=True,
            on_answer=self.get_target_pressure_action,
        )

    def _create_set_target_pressure_command_obj(self, pressure):
        return BaseCommand(
            command=BH_RRG_THROTTLE.THROTTLE_WRITE_TARGET_PRESSURE,
            arg1=pressure,
            with_answer=True,
            on_answer=self._on_simple_answer,
        )

    def _create_set_target_percent_command_obj(self, percent):
        return BaseCommand(
            command=BH_RRG_THROTTLE.THROTTLE_MOVE_TARGET_POSITION,
            arg1=percent / 100 * BH_RRG_THROTTLE.TOTAL_THROTTLE_STEPS,  # TODO: PERCENT TO STEPS AMOUNT!!!
            with_answer=True,
            on_answer=self._on_simple_answer,
        )

    @AbstractController.device_command()
    def set_target_sccm(self, sccm: float, device_num):
        sccm = float(sccm)
        max_sccm = self.get_max_sccm_device(device_num=device_num)
        sccm = min(max_sccm, max(0.0, sccm))
        assert 0.0 <= sccm <= max_sccm

        self.target_sccms[device_num] = sccm
        voltage_ratio = self._rrgs_config[device_num]['CONTROLLER_VOLTAGE_RATIO']
        sccm_shift = self._rrgs_config[device_num]['CONTROLLER_VOLTAGE_SHIFT']

        target_voltage = (sccm - sccm_shift) / max_sccm * self.max_rrg_voltage * voltage_ratio
        target_voltage = min(target_voltage, self.max_rrg_voltage)

        # target_flow = sccm / max_sccm * 100 * 100
        # print("CREATE SCCM TARGET COMMAND")

        self.add_command(BaseCommand(
            command=BH_RRG_THROTTLE.RRG_WRITE_VALUE,
            device_num=device_num,
            arg1=device_num,
            arg2=target_voltage,
            with_answer=True,
            on_answer=self._on_simple_answer,
        ))

        # print("NEW SCCM:", sccm, "| MAX:", max_sccm)
        return sccm

    @AbstractController.device_command()
    def full_rrg_open(self, device_num):
        max_sccm = self.get_max_sccm_device(device_num=device_num)
        return self.set_target_sccm(max_sccm, device_num)

    @AbstractController.device_command()
    def full_rrg_close(self, device_num):
        return self.set_target_sccm(0, device_num)
