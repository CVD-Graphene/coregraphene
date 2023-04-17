from ..communicators import AdcCommunicator, DacCommunicator
from .base import AbstractDevice


class RrgAdcDacDevice(AbstractDevice):
    _write_communicator_key = 'write'
    _read_communicator_key = 'read'

    def __init__(
            self,
            min_value=0,
            max_value=200,
            min_scale_value=0,
            max_scale_value=2**12 - 1,
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

        self.communicator = DacCommunicator(
            channel=self.kwargs.get('write_channel'),
            device=self.kwargs.get('write_device'),
            **kwargs,
        )
        self.write_communicator = self.communicator

        self.read_communicator = AdcCommunicator(
            channel=self.kwargs.get('read_channel'),
            device=self.kwargs.get('read_device'),
            **kwargs,
        )
        self.communicators_dict = {
            self._write_communicator_key: self.write_communicator,
            self._read_communicator_key: self.read_communicator,
        }

    def read(self, **kwargs):
        # print("R1")
        return super().read(_communicator_key=self._read_communicator_key, **kwargs)

    def exec_command(self, **kwargs):
        # print("START EXEC DEVICE")
        return super().exec_command(_communicator_key=self._write_communicator_key, **kwargs)

    def _preprocessing_value(self, value=0, **kwargs):
        # print("\n\n|>>> PREPR WRITE VALUE\n\n")
        return {
            'address': self.write_address,
            'value': int((max(self._min_value, min(value, self._max_value)) - self._min_value
                          ) / self._delta_value *
                         self._delta_scale_value + self._min_scale_value),
        }

    def _preprocessing_read_value(self, **kwargs) -> dict:
        # print("R2")
        return {
            'address': self.read_address,
            'value': 0,
        }

    def _postprocessing_value(self, value=0):
        # print("R10")
        try:
            # if len(value) >= 3:
            #     s = ''.join(map(lambda x: int2base(x).zfill(8), value[:3]))
            #     n = int(s[8:18], 2)
            total_value = int((
                    max(self._min_scale_value,
                        min(value, self._max_scale_value)) - self._min_scale_value
                              ) / self._delta_scale_value *
                     self._delta_value + self._min_value)
            print("POSTPROC VALUE:", value, total_value)
            return total_value
        except Exception as e:
            print("|> POSTROC RRG DEVICE ERROR:", e)

        return 0
