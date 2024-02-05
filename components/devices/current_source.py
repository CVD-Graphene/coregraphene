from ..communicators import SerialAsciiAkipCommunicator, InstekBaseSerialCommunicator
from ...conf import settings

from .base import AbstractDevice


class CurrentSourceDevice(AbstractDevice):
    communicator_class = SerialAsciiAkipCommunicator

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.communicator = self.communicator_class(
    #         *args,
    #         port_communicator=settings.ACCURATE_VAKUMETR_PORT,
    #         **kwargs,
    #     )
    #     self.kwargs = kwargs

    # def d_init_(self):
    #     super().__init__()
    #     self.communicator = SerialAsciiAkipCommunicator(
    #         port=settings.CURRENT_SOURCE_PORT
    #     )

    def _preprocessing_value(self, command=None, value=None):
        if value is None:
            return command.strip()
        return f"{command} {value}".strip()


class InstekCurrentSourceDevice(AbstractDevice):
    communicator_class = InstekBaseSerialCommunicator

    def _preprocessing_value(self, command=None, value=None):
        if value is None:
            return command.strip()
        return f"{command} {value}".strip()
