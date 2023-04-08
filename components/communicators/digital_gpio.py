from .base import AbstractCommunicator
from ..communication_methods import WiringDigitalMethod


class DigitalGpioCommunicator(AbstractCommunicator):
    communication_method_class = WiringDigitalMethod

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.communication_method = WiringDigitalMethod(
    #         **kwargs
    #     )
