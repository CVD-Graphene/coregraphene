from ..communicators import AdcDacCommunicator
from .base import AbstractDevice


class RrgAdcDacDevice(AbstractDevice):
    _write_communicator_key = 'write'
    _read_communicator_key = 'read'

    def __init__(
            self,
            min_value=0,
            max_value=200,
            min_scale_value=0,
            max_scale_value=1023,
            **kwargs):
        super().__init__(**kwargs)
        self.address = self.kwargs.get('address', 0)
        self.read_address = self.address
        self.write_address = self.address

        self._min_value = min_value
        self._max_value = max_value
        self._delta_value = self._max_value - self._min_value
        self._min_scale_value = min_scale_value
        self._max_scale_value = max_scale_value
        self._delta_scale_value = self._max_scale_value - self._min_scale_value

        self.communicator = AdcDacCommunicator(
            channel=self.kwargs.get('write_channel'),
            **kwargs,
        )
        self.write_communicator = self.communicator

        self.read_communicator = AdcDacCommunicator(
            channel=self.kwargs.get('read_channel'),
            **kwargs,
        )
        self.communicators_dict = {
            self._write_communicator_key: self.write_communicator,
            self._read_communicator_key: self.read_communicator,
        }

    def read(self, **kwargs):
        return super().read(_communicator_key=self._read_communicator_key, **kwargs)

    def exec_command(self, **kwargs):
        return super().read(_communicator_key=self._write_communicator_key, **kwargs)

    def _preprocessing_value(self, value=0, **kwargs):
        return {
            'address': self.write_address,
            'value': int((max(self._min_value, min(value, self._max_value)) - self._min_value) *
                         self._delta_scale_value + self._min_scale_value),
        }

    def _preprocessing_read_value(self, **kwargs) -> dict:
        return {
            'address': self.read_address,
            'value': 0,
        }

    def _postprocessing_value(self, value=0):
        try:
            # if len(value) >= 3:
            #     s = ''.join(map(lambda x: int2base(x).zfill(8), value[:3]))
            #     n = int(s[8:18], 2)
            total_value = int((
                    max(self._min_scale_value,
                        min(value, self._max_scale_value)) - self._min_scale_value) *
                     self._delta_value + self._min_value)
            print("POSTPROC VALUE:", value, total_value)
            return total_value
        except Exception as e:
            print("|> POSTROC RRG DEVICE ERROR:", e)

        return 0
