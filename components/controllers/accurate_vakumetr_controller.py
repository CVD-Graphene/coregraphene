from .base import AbstractController
from ..devices import AccurateVakumetrDevice


class AccurateVakumetrController(AbstractController):
    device_class = AccurateVakumetrDevice

    def destructor(self):
        super().destructor()
        print("|> Accurate vakumetr destructor!")

    def get_value(self):
        return self.device.get_value()

