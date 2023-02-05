# import wiringpi
from conf import settings
from exceptions.communication_methods import CommunicationMethodNotSetup

LOCAL_MODE = settings.LOCAL_MODE


class BaseCommunicationMethod:
    def __init__(self, *args, **kwargs):
        self.ready = False
        self.rs485 = None
        self._last_command = None
        self._last_read_value = None

    def setup(self, *args, **kwargs):
        self.ready = True

    def _check_setup(self):
        if not self.ready:
            raise CommunicationMethodNotSetup(
                communication_method_id=self.__class__.__name__
            )

    def send(self, *args, **kwargs):
        """Check mode and use _send method"""
        self._check_setup()

        if LOCAL_MODE:
            return self._local_send(*args, **kwargs)
        return self._send(*args, **kwargs)

    def _send(self, *args, **kwargs):
        raise NotImplementedError

    def _local_send(self, *args, **kwargs):
        return ""

    def read(self, *args, **kwargs):
        """Check mode and use _send method"""
        self._check_setup()

        if LOCAL_MODE:
            return self._local_read(*args, **kwargs)
        return self._read(*args, **kwargs)

    def _read(self, *args, **kwargs):
        raise NotImplementedError

    def _local_read(self, *args, **kwargs):
        return ""


# class ExampleBaseCommunicationMethod(BaseCommunicationMethod):
#     def setup(self, *args, **kwargs):
#         wiringpi.wiringPiSetup()
#
#     def send(self, *args, **kwargs):
#         wiringpi.pinMode(6, 1)
