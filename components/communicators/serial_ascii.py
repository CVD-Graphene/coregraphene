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


class BaseSerialAsciiCommunicator(AbstractCommunicator):
    communication_method_class = SerialAsciiCommunicationMethod

    def _preprocessing_value(self, value=""):
        # print("SEND WRITE VALUE COMMUN >>>>", value)
        return {
            "command": value,
        }

    # def _preprocessing_read_value(self, value=""):
    #     print("SEND READ VALUE COMMUN >>>>", value)
    #     return {
    #         "command": value,
    #     }

    # def __init__(self, port_communicator=None, **kwargs):
    #     super().__init__(**kwargs)
    #     self.port = port_communicator
    #     # self.communication_method = SerialAsciiCommunicationMethod(
    #     #     **kwargs,
    #     #     # port=ACCURATE_VAKUMETR_USB_PORT
    #     # )
    #     # self.communication_method = SerialAsciiCommunicationMethod()
    #
    # def _add_check_sum(self, command):
    #     summ = 0
    #     for c in command:
    #         summ += ord(c)
    #         # print(ord(c))
    #
    #     summ = (summ % 64) + 64
    #     # print(chr(summ))
    #     return f"{command}{chr(summ)}"
    #
    # def _preprocessing_value(self, value="0MV00"):
    #     address = str(self.port).zfill(self.ADDRESS_PORT_LEN)
    #     command = f"{address}{value}"
    #     command = f"{self._add_check_sum(command)}\r"
    #     # print("SerialAsciiCommunicator COMMAND::", command.strip())
    #     return {
    #         "command": command,
    #     }
    #
    # def _postprocessing_value(self, value: str = None):
    #     if LOCAL_MODE:
    #         return value
    #     # print("|>>>> VAK VALUE:", value)
    #     if value is None:
    #         value = ""
    #     answer = value.split('\r')[0]
    #     if len(answer) < 8:
    #         return ""
    #     ans_length = int(answer[6:8])
    #     return answer[8:8 + ans_length]


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


class SerialAsciiBhRrgControllerCommunicator(AbstractCommunicator):
    communication_method_class = SerialAsciiCommunicationMethod
    # ADDRESS_PORT_LEN = 3

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     # self.port = port_communicator
    #     # self.communication_method = SerialAsciiCommunicationMethod(
    #     #     **kwargs,
    #     #     # port=ACCURATE_VAKUMETR_USB_PORT
    #     # )
    #     # self.communication_method = SerialAsciiCommunicationMethod()

    def _add_check_sum(self, command):
        summ = 0
        for c in command:
            summ += ord(c)

        summ = (summ % 64) + 64
        # print(chr(summ))
        return f"{command} {chr(summ)}"

    def _preprocessing_value(self, value=None):
        # print('Get BH _preprocessing_value:', value)
        value = value or []
        value = ' '.join(map(str, value))
        # address = str(self.port).zfill(self.ADDRESS_PORT_LEN)
        command = f"{value}"
        # command = f"{self._add_check_sum(command)}"
        # print('BH _preprocessing_value command:', command)
        return {
            "command": command,
        }

    def _check_answer_sum(self, answer, check_sum):
        # TODO: сделать проверку
        return True

    def _postprocessing_value(self, value: str = None):
        if LOCAL_MODE:
            return ""
        # print("|>>>> BH_RRG_1 VALUE:", value, type(value))
        if value is None:
            return ""
            # value = ""
        answer = value.split('\n')[0]
        answer_split = answer.split()
        base_answer = ' '.join(answer_split[:-1])  # вообще [:-1]
        # print('base_answer', base_answer)
        # check_sum = answer_split[-1]
        # self._check_answer_sum(base_answer, check_sum)

        return base_answer


class InstekBaseSerialCommunicator(AbstractCommunicator):
    communication_method_class = SerialAsciiCommunicationMethod

    def _preprocessing_value(self, value="") -> dict:
        return {
            "command": f"{value}\r\n",
        }

    def _postprocessing_value(self, value: str = None):
        if not value:
            return ""
        return str(value).strip()
        # if LOCAL_MODE:
        #     return str(value).strip()

        # value = int(value[5:9], base=16) - 273
        # return value


class PumpTC110SerialAsciiCommunicator(AbstractCommunicator):
    communication_method_class = SerialAsciiCommunicationMethod
    ADDRESS_PORT_LEN = 3

    def __init__(self, port_communicator=None, **kwargs):
        super().__init__(**kwargs)
        self.port = port_communicator

    def _add_check_sum(self, command):
        summ = 0
        for c in command:
            summ += ord(c)
            # print(ord(c))

        summ = summ % 256
        return f"{command}{str(summ).zfill(3)}"

    def _preprocessing_value(self, value=""):
        address = str(self.port).zfill(self.ADDRESS_PORT_LEN)
        command = f"{address}{value}"
        command = f"{self._add_check_sum(command)}\r"  # {chr(13)} / \r
        # print('TC110 total command:', command)
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
        ans_length = int(answer[8:10])
        return answer[10:10 + ans_length]
