import gc

import minimalmodbus as mm
from .base import BaseCommunicationMethod
from ...conf import settings


class ModbusCommunicationMethod(BaseCommunicationMethod):
    def __init__(self,
                 port,  # f.e., '/dev/ttyUSB1'
                 mode,  # mm.MODE_ASCII/mm.MODE_RTU
                 instrument_number=None,  # f.e., 1 2 3...
                 baudrate=None,
                 timeout=None,
                 default_register_value=0,  # For LOCAL_MODE
                 ):
        """
        Save initial params for communication using modbus
        :param port: serial port, f.e. '/dev/ttyUSB1'
        :param mode: mm.MODE_ASCII or mm.MODE_RTU
        :param instrument_number: instrument number in connection (used in mm.Instrument),
            f.e. 1 2 3..., default settings `DEFAULT_MODBUS_INSTRUMENT_NUMBER`
        :param baudrate: default value in settings `DEFAULT_MODBUS_BAUDRATE` (19200)
        :param timeout: default value in settings `DEFAULT_MODBUS_TIMEOUT` (0.2)
        :param default_register_value: used in local mode for imitation of work state
        """

        super().__init__()
        self.port = port
        self.mode = mode

        self.instrument_number = instrument_number or settings.DEFAULT_MODBUS_INSTRUMENT_NUMBER
        self.baudrate = baudrate or settings.DEFAULT_MODBUS_BAUDRATE
        self.timeout = timeout or settings.DEFAULT_MODBUS_TIMEOUT

        print("|>>>> MODBUS: PORT=", port, "INST NUM:", self.instrument_number,
              "MODE", self.mode, "baudrate", self.baudrate)

        self.instrument = None

        # FOR LOCAL MODE
        self.last_register = None
        self.last_value = None
        self.last_precision = None
        self.last_functioncode = None
        self._default_register_value = default_register_value
        self.register_values = dict()

        self.communication_method_id = f"{self.__class__.__name__}: {self.port} " \
                                       f"{self.instrument_number}"

    def setup(self):
        super().setup()
        if settings.LOCAL_MODE:
            return

        self._create_instrument()

    def _create_instrument(self):
        self.instrument = mm.Instrument(
            self.port,
            self.instrument_number,
            close_port_after_each_call=False,
            mode=self.mode,
            debug=False
        ).serial.close()
        self.instrument.serial.baudrate = self.baudrate
        self.instrument.serial.timeout = self.timeout

        gc.collect()

    def _handle_exception(self, e):
        self.instrument.serial.close()
        self.instrument.serial.open()
        gc.collect()
        # self._create_instrument()

    def _send(self, register=None, value=None, precision=None, functioncode=None, **kwargs):
        last_command = f"{register} {value} {precision}"
        if functioncode is not None:
            last_command += f" {functioncode}"

        self._last_command = last_command

        args = [register, value]
        if precision is not None:
            args.append(precision)
        kwargs = dict()
        if functioncode is not None:
            kwargs['functioncode'] = functioncode
        self.instrument.write_register(*args, **kwargs)

    def _local_send(self, register=None, value=None, precision=None, functioncode=None, **kwargs):
        self.last_register = register
        self.last_value = value
        self.last_precision = precision
        self.last_functioncode = functioncode
        if precision is not None:
            value = value / float(10 ** (precision - 1))
        self.register_values[register] = value

    def _read(self, register=None, precision=None, **kwargs):
        last_command = f"{register} {precision}"

        self._last_command = last_command

        args = [register]
        if precision is not None:
            args.append(precision)
        # print("MODBUS _read ARGS:", args)
        answer = self.instrument.read_register(*args)
        return answer

    def _local_read(self, register=None, precision=None, **kwargs):
        answer = self.register_values.get(register, self._default_register_value)
        if precision is not None:
            answer /= 10 ** (precision - 1)
        return answer
