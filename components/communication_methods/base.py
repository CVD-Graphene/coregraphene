# import wiringpi
from conf import settings
from exceptions.communication_methods import CommunicationMethodNotSetup, BaseCommunicationMethodException

LOCAL_MODE = settings.LOCAL_MODE


class BaseCommunicationMethod:
    def __init__(self, *args, **kwargs):
        self.ready = False
        self.rs485 = None
        self._last_command = None
        self._last_read_value = None

        self.communication_method_id = self.__class__.__name__

    def setup(self, *args, **kwargs):
        self.ready = True

    def _check_setup(self):
        if not self.ready:
            raise CommunicationMethodNotSetup(
                communication_method_id=self.communication_method_id
            )

    def send(self, *args, **kwargs):
        """Check mode and use _send method"""
        self._check_setup()

        if LOCAL_MODE:
            return self._local_send(*args, **kwargs)
        try:
            return self._send(*args, **kwargs)
        except NotImplementedError:
            raise
        except Exception as e:
            raise BaseCommunicationMethodException(
                communication_method_id=self.communication_method_id,
                description=f"Write error: {str(e)}",
            ) from e

    def _send(self, *args, **kwargs):
        raise NotImplementedError

    def _local_send(self, *args, **kwargs):
        return ""

    def read(self, *args, **kwargs):
        """Check mode and use _send method"""
        self._check_setup()

        if LOCAL_MODE:
            return self._local_read(*args, **kwargs)

        try:
            return self._read(*args, **kwargs)
        except NotImplementedError:
            raise
        except Exception as e:
            raise BaseCommunicationMethodException(
                communication_method_id=self.communication_method_id,
                description=f"Read error: {str(e)}",
            ) from e

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
