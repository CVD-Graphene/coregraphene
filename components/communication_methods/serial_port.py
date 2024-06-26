import gc
import random
import time

import serial

from .base import BaseCommunicationMethod
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE
# SERIAL_PORT = settings.SERIAL_PORT


class SerialAsciiCommunicationMethod(BaseCommunicationMethod):
    def __init__(self,
                 port=None,
                 baudrate=19200,  # 115200 - was for vakumetr early
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS,
                 timeout=0.001,
                 pause=0.04,
                 create_instrument_delay=None,
                 immediate_serial_read=False,
                 **kwargs,
                 ):
        super().__init__()
        self.instrument = None

        self.port = port
        print("\n|#> SerialAsciiCommunicationMethod: port", port, ", baudrate", baudrate)
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.pause = pause
        self.create_instrument_delay = create_instrument_delay
        self.immediate_serial_read = immediate_serial_read

    def setup(self):
        super().setup()
        if LOCAL_MODE:
            return

        self._create_instrument()

    def _create_instrument(self):
        if settings.LOCAL_MODE:
            return

        self.instrument = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=self.timeout,
        )
        self.instrument.reset_input_buffer()
        self.instrument.reset_output_buffer()

        gc.collect()
        if self.create_instrument_delay:
            print('# SERIAL SLEEP', self.create_instrument_delay)
            time.sleep(self.create_instrument_delay)

    def update_communication(self, port=None, **kwargs):
        self.port = port or self.port
        self._create_instrument()

    def _handle_exception(self, e):
        try:
            self.instrument.reset_input_buffer()
            self.instrument.reset_output_buffer()

            self.instrument.close()
            self.instrument.reset_input_buffer()
            self.instrument.reset_output_buffer()

            self.instrument.open()
            time.sleep(0.5)
        except Exception as e2:
            print("SERIAL HANDLE ERR E2:", e2)

    def destructor(self):
        if LOCAL_MODE:
            return
        self.instrument.reset_input_buffer()
        self.instrument.reset_output_buffer()

        self.instrument.close()

    def _send(self, command=None):
        self._last_command = command
        # print("COMMAND SERIAL ASCII:", command)
        self.instrument.write(bytearray(command.encode("ASCII")))
        # if self.immediate_serial_read:
        #     self._last_read_value = self.instrument.readline()
        #     print('---------- LAST:', self._last_read_value)
            # print('|>> TEST:', self.instrument.readline())
        # sleep(self.pause)
        # sleep(1)
        # x = self.instrument.readline()
        # answer = x.decode('ASCII')
        # print("@ Q&A: ", command.strip(), " |", answer.strip())
        # return answer

    def _read(self, **kwargs):
        # if self.immediate_serial_read:
        #     x = self._last_read_value
        # else:
        x = self.instrument.readline()
        answer = x.decode('ASCII')
        # print("SERIAL ASCII READLINE:", answer)
        # print("@ Q&A: ", self._last_command.strip(), " |", answer.strip(), " | End")
        return answer

    def _local_read(self, *args, **kwargs):
        return round(random.random() * 100, 1)
