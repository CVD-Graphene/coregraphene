import minimalmodbus as mm

from .base import AbstractCommunicator
from ..communication_methods import ModbusCommunicationMethod


class ModbusRtuCommunicator(AbstractCommunicator):

    def __init__(self,
                 *args,
                 instrument_number=None,
                 baudrate=None,
                 timeout=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.communication_method = ModbusCommunicationMethod(
            port=self.port,
            mode=mm.MODE_RTU,
            instrument_number=instrument_number,
            baudrate=baudrate,
            timeout=timeout,
        )
