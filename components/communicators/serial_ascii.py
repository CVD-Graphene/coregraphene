from .base import AbstractCommunicator
from ..communication_methods import SerialAsciiCommunicationMethod
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE
ACCURATE_VAKUMETR_USB_PORT = settings.ACCURATE_VAKUMETR_USB_PORT


class SerialAsciiCommunicator(AbstractCommunicator):
    # communication_method_class = SerialAsciiCommunicationMethod
    ADDRESS_PORT_LEN = 3

    def __init__(self, *args, port_communicator=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.port = port_communicator
        self.communication_method = SerialAsciiCommunicationMethod(
            *args, **kwargs,
            # port=ACCURATE_VAKUMETR_USB_PORT
        )
        # self.communication_method = SerialAsciiCommunicationMethod()

    def _add_check_sum(self, command):
        summ = 0
        for c in command:
            summ += ord(c)
            # print(ord(c))

        summ = (summ % 64) + 64
        # print(chr(summ))
        return f"{command}{chr(summ)}"

    def _preprocessing_value(self, value="0MV00"):
        address = str(self.port).zfill(self.ADDRESS_PORT_LEN)
        command = f"{address}{value}"
        command = f"{self._add_check_sum(command)}\r"
        return {
            "command": command,
        }

    def _postprocessing_value(self, value: str = None):
        if LOCAL_MODE:
            return value

        if value is None:
            value = ""
        answer = value.split('\r')[0]
        if len(answer) < 8:
            return ""
        ans_length = int(answer[6:8])
        return answer[8:8 + ans_length]


class SerialAsciiAkipCommunicator(AbstractCommunicator):
    communication_method_class = SerialAsciiCommunicationMethod
    ADDRESS_PORT_LEN = 3

    def _preprocessing_value(self, value="0MV00") -> dict:
        return {
            "command": f"A{str(self.port).zfill(self.ADDRESS_PORT_LEN)}{value};\n",
        }

    def _postprocessing_value(self, value: str = None):
        # print("GET VAL POST PROC:", value, type(value))
        # if LOCAL_MODE or value is None:
        #     return ""
        return value.strip() if value else ""
