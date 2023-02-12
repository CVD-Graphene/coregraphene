from .base import AbstractCommunicator
from ..communication_methods import WiringDigitalMethod


class DigitalGpioCommunicator(AbstractCommunicator):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.communication_method = WiringDigitalMethod(
            port=self.port,
            **kwargs
        )
