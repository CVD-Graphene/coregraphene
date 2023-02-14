import random

from ...conf import settings

from .base import AbstractController
from ..commands import BaseCommand
from ..devices import AccurateVakumetrDevice

LOCAL_MODE = settings.LOCAL_MODE


class AccurateVakumetrController(AbstractController):
    device_class = AccurateVakumetrDevice

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vakumetr_value = None
        self.loop_delay = 0.5

        self._thread_using = True

    def _thread_setup_additional(self, **kwargs):
        self.add_command(BaseCommand(
            command="MV",
            value="00",
            repeat=True,
            with_answer=True,
            on_answer=self._on_get_vakumetr_value,
        ))

    @AbstractController.thread_command
    def _on_get_vakumetr_value(self, value):
        if LOCAL_MODE:
            value = random.random() * 100
        value = float(value)
        self.vakumetr_value = value
        # if self.on_change_voltage is not None:
        #     self.on_change_voltage(value)

    def destructor(self):
        super().destructor()
        print("|> Accurate vakumetr destructor!")

    def _check_command(self, **kwargs):
        value = self.device.get_value()
        assert value >= 0.0

    def get_value(self):
        return self.device.get_value()
