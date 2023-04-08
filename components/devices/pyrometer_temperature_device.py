from ..communicators import SerialAsciiSimpleCommunicator
from .base import AbstractDevice


class PyrometerTemperatureDevice(AbstractDevice):
    communicator_class = SerialAsciiSimpleCommunicator

    # def get_value_with_waiting(self):
    #     """For testing"""
    #     self.exec_command(command="MV", value="00")
    #     sleep(0.5)
    #     r = self.read()
    #     print("Read accurate vakumetr value:", r)#, "KW", self.kwargs)
    #     return r

    def _preprocessing_value(self, command=None):
        return command  # NO STRIP!!!!

    def _postprocessing_value(self, value=None):
        try:
            return float(value)
        except:
            return None
