from ..communicators import SerialAsciiBhRrgControllerCommunicator
from .base import AbstractDevice


class BhRrgDevice(AbstractDevice):
    communicator_class = SerialAsciiBhRrgControllerCommunicator

    def _preprocessing_value(self, command=None, arg1=None, arg2=None, **kwargs):
        answer = list(filter(lambda x: x is not None, [command, arg1, arg2]))
        return answer

    def _postprocessing_value(self, value=None):
        value = value or ""
        return value.strip().split(' ')
