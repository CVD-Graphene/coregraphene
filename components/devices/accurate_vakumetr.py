from time import sleep
from ...conf import settings

from ..communicators import SerialAsciiCommunicator
from .base import AbstractDevice


class AccurateVakumetrDevice(AbstractDevice):
    communicator_class = SerialAsciiCommunicator

    def __init__(self):
        super().__init__()
        self.communicator = self.communicator_class(
            port=settings.ACCURATE_VAKUMETR_PORT
        )

    def get_value(self):
        # return self.exec_command("MV", "00")
        self.exec_command("MV", "00")
        sleep(0.5)
        r = self.read()
        print("Read accurate vakumetr value:", r)
        return r

    def _postprocessing_value(self, value):
        try:
            return float(value)
        except:
            return None
