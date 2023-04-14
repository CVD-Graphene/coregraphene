from .base import AbstractCommunicator
from ..communication_methods import SpidevCommunicationMethod
from ...utils import int2base


class AdcDacCommunicator(AbstractCommunicator):
    communication_method_class = SpidevCommunicationMethod

    def _common_preprocessing_value(self, address=0, value=0, sending=False):
        # print("R4")
        n = 8

        device_base = int2base(address, base=2)
        value_base = int2base(min(2**12 - 1, value), base=2)
        start_bit = "0" # if sending else "1"
        #add_sending_str = "0" * n * 2
        add_str = "" #if sending else add_sending_str
        # print("Bases:", device_base, address, value_base, value)
        data_str = f"{start_bit}{device_base.zfill(3)}{value_base.zfill(12)}"  # + add_str

        # print("D1:", len(data_str))
        data = [int(data_str[i:i + n], 2) for i in range(0, len(data_str), n)]
        # print("ADC DAC DATA:", data_str, data)
        return {"data": data}

    def _preprocessing_value(self, **kwargs) -> dict:
        return self._common_preprocessing_value(sending=True, **kwargs)

    def _preprocessing_read_value(self, address=0, **kwargs) -> dict:
        # print("R3")
        n = 8

        device_address_base = int2base(address, base=2)
        start_bit = "1"
        # add_sending_str = "0" * n * 2
        # add_str = "" if sending else add_sending_str
        # print("Bases:", device_base, address, value_base, value)
        data_str = "0" * (n - 1) + "1" + \
                   f"{start_bit}{device_address_base.zfill(3)}" + "0000" + \
                   "0" * n

        # print("D1:", len(data_str))
        data = [int(data_str[i:i + n], 2) for i in range(0, len(data_str), n)]
        print("ADC DATA TO READ:", data_str, data)
        return {"data": data}
        # return self._common_preprocessing_value(sending=False, **kwargs)

    def _postprocessing_value(self, value=None):
        try:
            print("POSTPROC COMMUN SPI VALUE:", value)
            if len(value) >= 3:
                s = ''.join(map(lambda x: int2base(x).zfill(8), value[:3]))
                # print("S:::", s)
                n = int(s[14:24], 2)
                # print("POSTPROC VALUE COMMUNICATOR:", n)
                return n
        except Exception as e:
            print("POSTROC RRG ERROR:", e)

        return 0
