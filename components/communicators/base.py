from ..communication_methods import BaseCommunicationMethod
from ...constants import COMMUNICATION_INTERFACE_STATUS

from ...exceptions.communicators import (
    SetupCommunicatorException,
    InactiveCommunicatorException,
    BaseCommunicatorException,
    DoubleDeclarationMethodCommunicatorException,
)

from ...exceptions.communication_methods import BaseCommunicationMethodException


class AbstractCommunicator(object):
    communication_method_class = None

    def __init__(
            self,
            speed=None,
            port=None,
            communication_method: BaseCommunicationMethod = None,
            **kwargs
    ):
        self.communicator_id = self.__class__.__name__

        if communication_method is not None and\
                self.communication_method_class is not None:
            raise DoubleDeclarationMethodCommunicatorException(
                communicator_id=self.communicator_id
            )

        if communication_method is not None:
            self.communication_method: BaseCommunicationMethod = communication_method

        elif self.communication_method_class is not None:
            self.communication_method: BaseCommunicationMethod = self.communication_method_class()

        self.speed = speed
        self.port = port

        self._status = COMMUNICATION_INTERFACE_STATUS.INACTIVE
        self._errors = []
        # self.setup_configuration()

    def setup(self):
        try:
            self._status = COMMUNICATION_INTERFACE_STATUS.ACTIVE
            self.communication_method.setup()
        except BaseCommunicationMethodException:
            raise
        except Exception as e:
            self._errors.append(e)
            self._status = COMMUNICATION_INTERFACE_STATUS.HAS_ERRORS
            raise SetupCommunicatorException(
                communicator_id=self.communicator_id
            ) from e

    def destructor(self):
        self.communication_method.destructor()

    def is_valid(self, raise_exception=True):
        e = None
        if self._status == COMMUNICATION_INTERFACE_STATUS.INACTIVE:
            e = InactiveCommunicatorException(communicator_id=self.communicator_id)
            self._errors.append(e)
        elif self._status == COMMUNICATION_INTERFACE_STATUS.HAS_ERRORS:
            if bool(self._errors):
                e = self._errors[-1]
            else:
                self._status = COMMUNICATION_INTERFACE_STATUS.ACTIVE

        if e is not None and raise_exception:
            raise e

        return not bool(self._errors)

    def send(self, raise_exception=True, **kwargs):
        """
        preprocess value -> send value -> get answer -> answer processing ->
        1. has mistakes -> raise error
        2. all oKey -> return value
        :return:
        """
        self.is_valid(raise_exception=raise_exception)

        try:
            preprocessing_ans: dict = self._preprocessing_value(**kwargs)
            if type(preprocessing_ans) != dict:
                preprocessing_ans = {"value": preprocessing_ans}

            answer = self.communication_method.send(**preprocessing_ans)
            return self._postprocessing_value(answer)
        except (BaseCommunicationMethodException, AssertionError):
            raise
        except Exception as e:
            return self._handle_exception(e)

    def read(self, raise_exception=True, **kwargs):
        self.is_valid(raise_exception=raise_exception)

        try:
            answer = self.communication_method.read(**kwargs)
            return self._postprocessing_value(answer)
        except BaseCommunicationMethodException:
            raise
        except Exception as e:
            return self._handle_exception(e)

    def _preprocessing_value(self, **kwargs) -> dict:
        # ans = dict(kwargs)
        # ans["value"] = value
        # return ans
        return kwargs

    def _postprocessing_value(self, value=None):
        """
        Is answer is oKey?
        1. Answer OK ? -> _extract_value
        2. Else -> _handle_exception
        :return:
        """
        # ans = dict(kwargs)
        # ans["value"] = value
        # return ans
        return value

    def _handle_exception(self, e):
        raise BaseCommunicatorException(
            communicator_id=self.communicator_id,
            description=str(e),
        ) from e
