from ..communicators import SerialAsciiAkipCommunicator
from ...conf import settings

from .base import AbstractDevice


class CurrentSourceDevice(AbstractDevice):
    def __init__(self):
        super().__init__()
        self.communicator = SerialAsciiAkipCommunicator(
            port=settings.CURRENT_SOURCE_PORT
        )

    def _preprocessing_value(self, command, value):
        if value is None:
            return command.strip()
        return f"{command} {value}".strip()
