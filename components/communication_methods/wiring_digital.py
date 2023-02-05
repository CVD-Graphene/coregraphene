try:
    import wiringpi
except:
    pass

from .base import BaseCommunicationMethod
# from ...settings import LOCAL_MODE
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class WiringDigitalMethod(BaseCommunicationMethod):
    def __init__(self,
                 port,
                 default_command=1,
                 ):
        super().__init__()
        self.port = port
        self.default_command = default_command

    def setup(self):
        super().setup()
        if LOCAL_MODE:
            return
        wiringpi.wiringPiSetupGpio()  # For GPIO pin numbering
        wiringpi.wiringPiSetup()  # For sequential pin numbering
        wiringpi.pinMode(self.port, 1)  # Set pin 6 to 1 ( OUTPUT )
        if self.default_command is not None:
            wiringpi.digitalWrite(self.port, self.default_command)  # Write 1 ( HIGH ) to pin 6

    def _send(self, command):
        wiringpi.digitalWrite(self.port, command)  # Write 1 ( HIGH ) to pin 6
        read_value = wiringpi.digitalRead(self.port)  # Read pin 6
        self._last_read_value = read_value
        return read_value

    def _read(self, *args, **kwargs):
        return self._last_read_value
