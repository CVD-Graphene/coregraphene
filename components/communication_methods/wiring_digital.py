try:
    import wiringpi
except:
    pass

from .base import BaseCommunicationMethod
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE
DEFAULT_PIN_VALUE = 0


class WiringDigitalMethod(BaseCommunicationMethod):
    def __init__(self,
                 port,
                 default_command=None,
                 **kwargs,
                 ):
        super().__init__()
        self.port = port
        self.default_command = default_command

        # FOR LOCAL IMITATION
        self._ports = dict()

    def setup(self):
        super().setup()

        if LOCAL_MODE:
            if self.default_command is not None:
                self._ports[self.port] = self.default_command
            return

        wiringpi.wiringPiSetupGpio()  # For GPIO pin numbering
        wiringpi.wiringPiSetup()  # For sequential pin numbering

        wiringpi.pinMode(self.port, 1)  # Set pin 6 to 1 ( OUTPUT )
        if self.default_command is not None:
            wiringpi.digitalWrite(self.port, self.default_command)  # Write 1 ( HIGH ) to pin 6

    def _local_send(self, command=None):
        self._ports[self.port] = command
        self._last_read_value = command
        return command

    def _send(self, command=None):
        wiringpi.digitalWrite(self.port, command)  # Write 1 ( HIGH ) to pin 6
        read_value = wiringpi.digitalRead(self.port)  # Read pin 6
        self._last_read_value = read_value
        return read_value

    def _read(self, *args, **kwargs):
        return self._last_read_value

    def _local_read(self, *args, **kwargs):
        return self._last_read_value
