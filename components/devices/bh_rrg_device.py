from ..communicators import SerialAsciiBhRrgControllerCommunicator
from .base import AbstractDevice


class BhRrgDevice(AbstractDevice):
    communicator_class = SerialAsciiBhRrgControllerCommunicator

    def _preprocessing_value(self, arg1=None, arg2=None):
        answer = list(filter(lambda x: x is not None, [arg1, arg2]))
        return answer

    def _postprocessing_value(self, value=None):
        value = value or ""
        return value.strip().split(' ')
