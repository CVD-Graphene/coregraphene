from ...communicators import ModbusRtuCommunicator
from ..base import AbstractDevice


class BaseModbusRtuDevice(AbstractDevice):
    communicator_class = ModbusRtuCommunicator

    # def _preprocessing_value(self, register=None, value=None, **kwargs):
    #     return {
    #         'register': register,
    #         'value': value,
    #         **kwargs,
    #     }
