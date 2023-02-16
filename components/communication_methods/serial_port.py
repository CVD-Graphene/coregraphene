import random
import serial

from .base import BaseCommunicationMethod
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE
SERIAL_PORT = settings.SERIAL_PORT


class SerialAsciiCommunicationMethod(BaseCommunicationMethod):
    def __init__(self,
                 port=SERIAL_PORT,
                 baudrate=19200,  # 115200 - was for vakumetr early
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 bytesize=serial.EIGHTBITS,
                 timeout=0.001,
                 pause=0.04,
                 ):
        super().__init__()
        self.port = port
        print("\n|#> SerialAsciiCommunicationMethod: port", port, ", baudrate", baudrate)
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.pause = pause

    def setup(self):
        super().setup()
        if LOCAL_MODE:
            return

        self.rs485 = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            parity=self.parity,
            stopbits=self.stopbits,
            bytesize=self.bytesize,
            timeout=self.timeout,
        )

    def destructor(self):
        if LOCAL_MODE:
            return
        self.rs485.close()

    def _send(self, command=None):
        # if LOCAL_MODE:
        #     return
        #     # return "0011MV079.999e2u"
        self._last_command = command
        self.rs485.write(bytearray(command.encode("ASCII")))
        # sleep(self.pause)
        # sleep(1)
        # x = self.rs485.readline()
        # answer = x.decode('ASCII')
        # print("@ Q&A: ", command.strip(), " |", answer.strip())
        # return answer

    def _read(self, **kwargs):
        x = self.rs485.readline()
        answer = x.decode('ASCII')
        # print("@ Q&A: ", self._last_command.strip(), " |", answer.strip(), " | End")
        return answer

    def _local_read(self, *args, **kwargs):
        return round(random.random() * 100, 1)
