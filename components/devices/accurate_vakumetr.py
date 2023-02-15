from time import sleep
from ...conf import settings

from ..communicators import SerialAsciiCommunicator
from .base import AbstractDevice


class AccurateVakumetrDevice(AbstractDevice):
    communicator_class = SerialAsciiCommunicator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.communicator = self.communicator_class(
            *args,
            port_communicator=settings.ACCURATE_VAKUMETR_PORT,
            **kwargs,
        )
        self.kwargs = kwargs

    def get_value(self):
        # return self.exec_command("MV", "00")
        # self.exec_command(command="MV", value="00")
        # sleep(0.5)
        r = self.read()
        print("Read accurate vakumetr value:", r)
        return r

    def get_value_with_waiting(self):
        """For testing"""
        self.exec_command(command="MV", value="00")
        sleep(1)
        r = self.read()
        print("Read accurate vakumetr value:", r)#, "KW", self.kwargs)
        return r

    def _preprocessing_value(self, operation_code="0", command=None, value=None):
        return f"{operation_code}{command}{value}".strip()

    def _postprocessing_value(self, value=None):
        try:
            return float(value)
        except:
            return None
