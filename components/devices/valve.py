from .base import AbstractDevice
from ..communicators import DigitalGpioCommunicator


class ValveDevice(AbstractDevice):
    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)
        self.communicator = DigitalGpioCommunicator(
            port=port,
            **kwargs,
        )

    def _preprocessing_value(self, command=None):
        return {"command": command}
