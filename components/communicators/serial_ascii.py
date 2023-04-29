from .base import AbstractCommunicator
from ..communication_methods import SerialAsciiCommunicationMethod
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE


class SerialAsciiCommunicator(AbstractCommunicator):
    communication_method_class = SerialAsciiCommunicationMethod
    ADDRESS_PORT_LEN = 3

    def __init__(self, port_communicator=None, **kwargs):
        super().__init__(**kwargs)
        self.port = port_communicator
        # self.communication_method = SerialAsciiCommunicationMethod(
        #     **kwargs,
        #     # port=ACCURATE_VAKUMETR_USB_PORT
        # )
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
        # print("SerialAsciiCommunicator COMMAND::", command.strip())
        return {
            "command": command,
        }

    def _postprocessing_value(self, value: str = None):
        if LOCAL_MODE:
            return value
        # print("|>>>> VAK VALUE:", value)
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

    def __init__(self, port_communicator=None, **kwargs):
        super().__init__(**kwargs)
        self.port = port_communicator
        # self.communication_method = SerialAsciiCommunicationMethod(
        #     *args, **kwargs,
        # )

    def _preprocessing_value(self, value="0MV00") -> dict:
        # print("SerialAsciiAkipCommunicator VALUE:", value)
        command = f"A{str(self.port).zfill(self.ADDRESS_PORT_LEN)}{value};\n"
        # print("SerialAsciiAkipCommunicator COMMAND::", command.strip())
        return {
            "command": command,
        }

    def _postprocessing_value(self, value: str = None):
        # print("SerialAsciiAkipCommunicator ANSWER::", value, type(value))
        # if LOCAL_MODE or value is None:
        #     return ""
        value = str(value)
        return value.strip() if value else ""


class SerialAsciiPyrometerCommunicator(AbstractCommunicator):
    communication_method_class = SerialAsciiCommunicationMethod

    def _preprocessing_value(self, value="") -> dict:
        # print("VALUE", value)
        return {
            "command": value,
        }

    def _postprocessing_value(self, value: str = None):
        if not value:
            return ""
        if LOCAL_MODE:
            return str(value).strip()

        value = int(value[5:9], base=16) - 273
        return value
