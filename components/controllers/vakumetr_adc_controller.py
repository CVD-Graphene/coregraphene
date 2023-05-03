from ...system_effects import GetCurrentPressureVakumetrAdcControllerEffect
from .base import AbstractControllerManyDevices
from ..commands import BaseCommand
from ..devices import VakumetrAdcDevice


class VakumetrAdcController(AbstractControllerManyDevices):
    code = 'vakumetr_adc'

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)

        self._thread_using = True
        self._vakumetr_config = config

        self.devices = []
        for vakumetr_config in config:
            vakumetr = VakumetrAdcDevice(
                address=vakumetr_config['VAKUMETR_ADDRESS'],
                **kwargs,
            )
            self.devices.append(vakumetr)
            # break

        self.devices_amount = len(self.devices)
        self.loop_delay = 0.3

        self.current_pressures = [0.0 for _ in self.devices]
        self.get_current_pressure_action = GetCurrentPressureVakumetrAdcControllerEffect(controller=self)

    def _thread_setup_additional(self, **kwargs):
        for i in range(self.devices_amount):
            self.add_command(BaseCommand(
                device_num=i,
                repeat=True,
                immediate_answer=True,
                on_answer=self.get_current_pressure_action,
            ))
