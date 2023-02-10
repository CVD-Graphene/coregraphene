import minimalmodbus as mm
from .base import BaseCommunicationMethod
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class ModbusCommunicationMethod(BaseCommunicationMethod):
    def __init__(self,
                 port,  # f.e., '/dev/ttyUSB1'
                 instrument_number,  # f.e., 1 2 3...
                 mode,  # mm.MODE_ASCII/mm.MODE_RTU
                 baudrate=19200,
                 timeout=0.2,
                 default_register_value=0,  # For LOCAL_MODE
                 ):
        super().__init__()
        self.port = port
        self.instrument_number = instrument_number
        self.mode = mode
        self.baudrate = baudrate
        self.timeout = timeout

        self.instrument = None

        # FOR LOCAL MODE
        self.last_register = None
        self.last_value = None
        self.last_precision = None
        self.last_functioncode = None
        self._default_register_value = default_register_value
        self.register_values = dict()

    def setup(self):
        super().setup()
        if LOCAL_MODE:
            return

        self.instrument = mm.Instrument(
            self.port,
            self.instrument_number,
            debug=False
        )
        self.instrument.serial.baudrate = self.baudrate
        self.instrument.serial.timeout =self.timeout
        self.instrument.mode = mm.MODE_ASCII

    def _send(self, register, value, precision=1, functioncode=None):
        last_command = f"{register} {value} {precision}"
        if functioncode is not None:
            last_command += f" {functioncode}"

        self._last_command = last_command
        self.instrument.write_register(register, value, precision)

    def _local_send(self, register, value, precision=1, functioncode=None):
        self.last_register = register
        self.last_value = value
        self.last_precision = precision
        self.last_functioncode = functioncode
        self.register_values[register] = value / float(10 ** (precision - 1))

    def _read(self, register, precision=1):
        answer = self.instrument.read_register(register, precision)
        return answer

    def _local_read(self, register, precision=1):
        answer = self.register_values.get(register, self._default_register_value)
        answer /= 10 ** (precision - 1)
        return answer
