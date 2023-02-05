from .base import AbstractDevice
from ..communicators import DigitalGpioCommunicator


class ValveDevice(AbstractDevice):
    def __init__(self, port):
        super().__init__()
        self.communicator = DigitalGpioCommunicator(port=port)

    def _preprocessing_value(self, command, value=None):
        return command
