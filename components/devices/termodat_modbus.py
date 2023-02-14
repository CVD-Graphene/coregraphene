from time import sleep
from ...conf import settings

from ..communicators import ModbusAsciiCommunicator
from .base import AbstractDevice

PRECISION = 1
REGISTER_ON_OFF = 384  # Register for on/off device
ON, OFF = 1, 0
REGISTER_CURRENT_TEMPERATURE_GET = 368
REGISTER_TARGET_TEMPERATURE_GET = 369  # 48 - too
REGISTER_TARGET_TEMPERATURE_SET = 371
REGISTER_SPEED_SET = 377


class TermodatModbusDevice(AbstractDevice):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get('baudrate', None) is None:
            kwargs['baudrate'] = settings.DEFAULT_MODBUS_TERMODAT_BAUDRATE
        self.communicator = ModbusAsciiCommunicator(
            **kwargs,
        )

    def _preprocessing_value(self, **kwargs):
        if kwargs.get("precision", None) is None:
            kwargs['precision'] = PRECISION
        return kwargs
