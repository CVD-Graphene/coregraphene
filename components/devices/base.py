import traceback

from ..communicators import AbstractCommunicator
from ...constants import DEVICE_STATUS
from ...exceptions.communication_methods import BaseCommunicationMethodException
from ...exceptions.communicators import BaseCommunicatorException
from ...exceptions.devices import (
    BaseDeviceException,
    SetupDeviceException,
    InactiveDeviceException,
    # DoubleDeclarationCommunicatorException,
)


class AbstractDevice(object):
    """
    Device class with base method `exec_command`

    """
    communicator_class: AbstractCommunicator = None
    default_communicator_key = 'default'

    def __init__(
            self,
            # communicator: AbstractCommunicator = None,
            **kwargs,
    ):
        # if communicator is not None and self.communicator_class is not None:
        #     raise DoubleDeclarationCommunicatorException(device_id=self.__class__.__name__)

        # if communicator:
        #     self.communicator: AbstractCommunicator = communicator
        self.communicator = None

        self.kwargs = kwargs
        self.communicators_dict = {}

        if self.communicator_class is not None:
            self.communicator: AbstractCommunicator = self.communicator_class(
                **kwargs,
            )
        self._last_command = None
        self._status = DEVICE_STATUS.INACTIVE
        self._errors = []

        self.device_id = self.__class__.__name__

    def setup(self):
        try:
            if len(self.communicators_dict.keys()) == 0:
                self.communicators_dict[self.default_communicator_key] = self.communicator

            for communicator in self.communicators_dict.values():
                communicator.setup()
            #self.communicator.setup()
            self._status = DEVICE_STATUS.ACTIVE
        except (BaseCommunicatorException, BaseCommunicationMethodException):
            raise
        except Exception as e:
            self._status = DEVICE_STATUS.HAS_ERRORS
            self._errors.append(e)
            raise SetupDeviceException(device_id=self.device_id) from e

    def destructor(self):
        for communicator in self.communicators_dict.values():
            communicator.destructor()
        # self.communicator.destructor()

    def update_communication(self, **kwargs):
        for communicator in self.communicators_dict.values():
            communicator.update_communication(**kwargs)
        # self.communicator.update_communication(**kwargs)

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
    def exec_command(self, _communicator_key=None, **kwargs):
        """
        Main function for execution user commands
        :param _communicator_key: key for using communicator from local dict, left None for using default
        :return:
        """
        self.is_valid()

        command = kwargs.get("command", None)
        # value = kwargs.get("value", None)

        self._last_command = command
        try:
            if _communicator_key is None:
                _communicator_key = self.default_communicator_key
            communicator = self.communicators_dict.get(_communicator_key)

            preprocessing_ans = self._preprocessing_value(**kwargs)
            if type(preprocessing_ans) != dict:
                preprocessing_ans = {"value": preprocessing_ans}
            answer = communicator.send(**preprocessing_ans)

            return self._postprocessing_value(answer)

        except (BaseCommunicatorException, BaseCommunicationMethodException):
            raise

        except Exception as e:
            s = traceback.format_exc()
            print("MY COOL DEVICE ERROR", s)
            return self._handle_exception(e)

    def read(self, _communicator_key=None, **kwargs):
        self.is_valid()

        try:
            if _communicator_key is None:
                _communicator_key = self.default_communicator_key
            communicator = self.communicators_dict.get(_communicator_key)

            preprocessing_ans = self._preprocessing_read_value(**kwargs)
            return self._postprocessing_value(
                communicator.read(**preprocessing_ans)
            )

        except (BaseCommunicatorException, BaseCommunicationMethodException):
            raise

        except Exception as e:
            s = traceback.format_exc()
            print("|> READ ERROR DEVICE", s)
            return self._handle_exception(e)

    def _handle_exception(self, e: Exception):
        raise BaseDeviceException(device_id=self.device_id) from e

    def _preprocessing_value(self, **kwargs):
        """
        Connect command with value to one meaning to send for communication interface
        :param command:
        :param value:
        :return:
        """
        return kwargs
        # command = kwargs.get("command", None)
        # value = kwargs.get("value", None)
        #
        # ans = dict(kwargs)
        # if command is not None and value is not None:
        #     ans["value"] = f"{command}{value}".strip(),
        # return ans

    def _preprocessing_read_value(self, **kwargs) -> dict:
        return kwargs

    def _postprocessing_value(self, value=None):
        return value

    def __str__(self):
        return f"Device {self.__class__.__name__}"
