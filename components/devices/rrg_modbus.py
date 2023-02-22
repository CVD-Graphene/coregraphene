from time import sleep
from ...conf import settings

from ..communicators import ModbusRtuCommunicator
from .base import AbstractDevice

REGISTER_STATE_FLAGS_1 = 2
REGISTER_STATE_FLAGS_1_MIN_MASK = 0b10011


class RrgModbusDevice(AbstractDevice):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.communicator = ModbusRtuCommunicator(
            **kwargs,
            # port=settings.RRG_MODBUS_DEVICE_PORT,
        )

    def _preprocessing_value(self, register=None, value=None, **kwargs):
        # if register == REGISTER_STATE_FLAGS_1:
        #     value = value | REGISTER_STATE_FLAGS_1_MIN_MASK
        return {
            'register': register,
            'value': value,
            **kwargs,
        }
