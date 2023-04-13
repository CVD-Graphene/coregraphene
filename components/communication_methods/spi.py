import gc
import random

try:
    import spidev
except Exception as e:
    pass
    # print("Spidev import error:", e)

from .base import BaseCommunicationMethod
from ...conf import settings


class SpidevCommunicationMethod(BaseCommunicationMethod):
    def __init__(self,
                 channel=None,  # f.e., 0
                 speed=None,  # 2000
                 device=None,  # f.e., 0 1 2...
                 default_register_value=0,  # For LOCAL_MODE
                 **kwargs
                 ):
        """
        Save initial params for communication using spidev
        :param channel: int spi channel, f.e. 0
        :param speed: spi communication speed, f.e. 20000
        :param device: device number in connection, f.e. 0 1...,
        :param default_register_value: used in local mode for imitation of work state
        """

        super().__init__()
        self.channel = channel
        # self.mode = mode
        self.speed = speed or 20000

        self.device = device or 0
        # self.timeout = timeout or settings.DEFAULT_MODBUS_TIMEOUT

        # print("|>>>> MODBUS: PORT=", port, "INST NUM:", self.instrument_number,
        #       "MODE", self.mode, "baudrate", self.baudrate)

        self.instrument = None

        # FOR LOCAL MODE
        self.last_register = None
        self.last_value = None
        self._default_register_value = default_register_value
        self.register_values = dict()

        self.communication_method_id = f"{self.__class__.__name__}: {self.channel} " \
                                       f"{self.device}"

    def setup(self):
        super().setup()
        if settings.LOCAL_MODE:
            return

        self._create_instrument()

    def _create_instrument(self):
        if settings.LOCAL_MODE:
            return

        # self.spi = spidev.SpiDev()
        self.instrument = spidev.SpiDev()
        print("SPI CI:::", self.channel, type(self.channel), self.device, type(self.device))
        self.instrument.open(self.channel, self.device)  # device 0, 1 - выбор чипа
        self.instrument.max_speed_hz = self.speed

        self.instrument.lsbfirst = False
        self.instrument.bits_per_word = 8
        # self.instrument.mode = 0b01
        # print("spi.mode = " + str(spi.mode))
        self.instrument.cshigh = False

        # gc.collect()

    def update_communication(self, **kwargs):
        self._create_instrument()

    def _send(self, data=None, **kwargs):
        assert type(data) == list
        _data = data.copy()
        answer = self.instrument.xfer(_data)
        return answer

    def _local_send(self, data=None, **kwargs):
        _data = data.copy()
        return _data

    def _read(self, data=None, **kwargs):
        assert type(data) == list
        _data = data.copy()
        answer = self.instrument.xfer(_data)
        return answer

    def _local_read(self, data=None, **kwargs):
        _data = data.copy()
        return [
            0,
            random.randint(0, 1023),
            random.randint(0, 1) * 512 +
            random.randint(0, 1) * 256 +
            random.randint(0, 128),
            random.randint(0, 1023),
        ]
        # return _data
