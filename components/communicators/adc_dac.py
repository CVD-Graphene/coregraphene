from .base import AbstractCommunicator
from ..communication_methods import SpidevCommunicationMethod
from ...utils import int2base


class AdcDacCommunicator(AbstractCommunicator):
    communication_method_class = SpidevCommunicationMethod

    def _common_preprocessing_value(self, address=0, value=0):
        # print("R4")
        n = 8

        device_base = int2base(address, base=2)
        value_base = int2base(min(1023, value), base=2)
        # print("Bases:", device_base, address, value_base, value)
        data_str = f"1{device_base.zfill(3)}{value_base.zfill(10)}00" + "0" * n * 2

        # print("D1:", len(data_str))
        data = [int(data_str[i:i + n], 2) for i in range(0, len(data_str), n)]
        # print("ADC DAC DATA:", data_str, data)
        return {"data": data}

    def _preprocessing_value(self, **kwargs) -> dict:
        return self._common_preprocessing_value(**kwargs)

    def _preprocessing_read_value(self, **kwargs) -> dict:
        # print("R3")
        return self._common_preprocessing_value(**kwargs)

    def _postprocessing_value(self, value=None):
        try:
            print("POSTPROC COMMUN SPI VALUE:", value)
            if len(value) >= 3:
                s = ''.join(map(lambda x: int2base(x).zfill(8), value[:3]))
                # print("S:::", s)
                n = int(s[8:18], 2)
                # print("POSTPROC VALUE COMMUNICATOR:", n)
                return n
        except Exception as e:
            print("POSTROC RRG ERROR:", e)

        return 0