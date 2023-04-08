from .base import AbstractDevice
from ..communicators import DigitalGpioCommunicator


class ValveDevice(AbstractDevice):
    communicator_class = DigitalGpioCommunicator

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.communicator = DigitalGpioCommunicator(
    #         # port=port,
    #         **kwargs,
    #     )

    def _preprocessing_value(self, command=None):
        return {"command": command}
