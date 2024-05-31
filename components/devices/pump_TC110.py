from ..communicators import PumpTC110SerialAsciiCommunicator
from .base import AbstractDevice


class PumpTC110Device(AbstractDevice):
    communicator_class = PumpTC110SerialAsciiCommunicator

    def _preprocessing_value(self, command=None, value=None):
        read = False
        if value is None:
            value = "=?"
            read = True
        value = str(value)
        code = "00" if read else "10"
        data_len = str(len(value)).zfill(2)
        return f"{code}{command}{data_len}{value}".strip()

    def _postprocessing_value(self, value=None):
        try:
            return float(value)
        except:
            return None
