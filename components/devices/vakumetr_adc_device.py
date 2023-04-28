from ..communicators import AdcCommunicator
from .base import AbstractDevice


class VakumetrAdcDevice(AbstractDevice):
    communicator_class = AdcCommunicator

    def __init__(
            self,
            min_value=0.0,
            max_value=10.0,
            min_target_value=2**10 // 5,
            max_target_value=2**10 - 1,
            **kwargs):
        super().__init__(**kwargs)
        self.address = self.kwargs.get('address', 0)
        # self.read_address = self.address
        # self.write_address = self.address

        self._min_value = min_value
        self._max_value = max_value
        self._delta_value = self._max_value - self._min_value
        self._min_target_value = min_target_value
        self._max_target_value = max_target_value
        self._delta_target_value = self._max_target_value - self._min_target_value

        # self.read_communicator = AdcCommunicator(
        #     channel=self.kwargs.get('read_channel'),
        #     device=self.kwargs.get('read_device'),
        #     **kwargs,
        # )

    # def _preprocessing_read_value(self, **kwargs) -> dict:
    #     # print("R2")
    #     return {
    #         'address': self.read_address,
    #         'value': 0,
    #     }

    def _postprocessing_value(self, value=0):
        # print("R10")
        try:
            total_value = float((
                    max(self._min_target_value,
                        min(value, self._max_target_value)) - self._min_target_value
                              ) / self._delta_target_value *
                     self._delta_value + self._min_value)
            # print("POSTPROC VALUE:", value, total_value)
            return total_value
        except Exception as e:
            print("|> POSTROC VAKUM ADC DEVICE ERROR:", e)

        return 0
