import traceback

from components.communicators import AbstractCommunicator
from constants import DEVICE_STATUS
from exceptions.communication_methods import BaseCommunicationMethodException
from exceptions.communicators import BaseCommunicatorException
from exceptions.devices import (
    BaseDeviceException,
    SetupDeviceException,
    InactiveDeviceException,
    DoubleDeclarationCommunicatorException,
)


class AbstractDevice(object):
    """
    Device class with base method `exec_command`

    """
    communicator_class: AbstractCommunicator = None

    def __init__(
            self,
            communicator: AbstractCommunicator = None,
    ):
        # if communicator is not None and self.communicator_class is not None:
        #     raise DoubleDeclarationCommunicatorException(device_id=self.__class__.__name__)

        if communicator:
            self.communicator: AbstractCommunicator = communicator
        elif self.communicator_class is not None:
            self.communicator: AbstractCommunicator = self.communicator_class()
        self._last_command = None
        self._status = DEVICE_STATUS.INACTIVE
        self._errors = []

        self.device_id = self.__class__.__name__

    def setup(self):
        try:
            self.communicator.setup()
            self._status = DEVICE_STATUS.ACTIVE
        except (BaseCommunicatorException, BaseCommunicationMethodException):
            raise
        except Exception as e:
            self._status = DEVICE_STATUS.HAS_ERRORS
            self._errors.append(e)
            raise SetupDeviceException(device_id=self.device_id) from e

    def destructor(self):
        pass

    def is_valid(self, raise_exception=True):
        e = None
        if self._status == DEVICE_STATUS.INACTIVE:
            e = InactiveDeviceException(device_id=self.device_id)
            self._errors.append(e)
        elif self._status == DEVICE_STATUS.HAS_ERRORS:
            if bool(self._errors):
                e = self._errors[-1]
            else:
                self._status = DEVICE_STATUS.ACTIVE

        if e is not None and raise_exception:
            raise e

        return not bool(self._errors)

    # def on/off/
    def exec_command(self, command, value=None):
        """
        Main function for execution user commands
        :param command:
        :param value:
        :return:
        """
        self.is_valid()

        self._last_command = command
        try:
            preprocessing_value = self._preprocessing_value(command, value)
            answer = self.communicator.send(preprocessing_value)

            return self._postprocessing_value(answer)

        except (BaseCommunicatorException, BaseCommunicationMethodException):
            raise

        except Exception as e:
            s = traceback.format_exc()
            print(s)
            return self._handle_exception(e)

    def read(self):
        self.is_valid()

        try:
            return self._postprocessing_value(
                self.communicator.read()
            )

        except (BaseCommunicatorException, BaseCommunicationMethodException):
            raise

        except Exception as e:
            s = traceback.format_exc()
            print("|> READ ERROR DEVICE", s)
            return self._handle_exception(e)

    def _handle_exception(self, e: Exception):
        raise BaseDeviceException(device_id=self.device_id) from e

    def _preprocessing_value(self, command, value):
        """
        Connect command with value to one meaning to send for communication interface
        :param command:
        :param value:
        :return:
        """
        return f"{command}{value}".strip()

    def _postprocessing_value(self, value):
        return value
