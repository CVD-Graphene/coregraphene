from .base import AbstractController
from ..devices import RrgModbusDevice
from ...conf import settings

LOCAL_MODE = settings.LOCAL_MODE

CLOSE = 1
OPEN = 0

OPEN_RRG_FLAGS = 0b1100
CLOSE_RRG_FLAGS = 0b1000
REGISTER_STATE_FLAGS_1 = 2
REGISTER_SET_FLOW = 4
REGISTER_GET_FLOW = REGISTER_SET_FLOW if LOCAL_MODE else 5


class RrgModbusController(AbstractController):
    def __init__(self, **kwargs):
        super().__init__()
        self.device = RrgModbusDevice(
            **kwargs
        )
        self.is_open = False
        self.target_sccm = 0.0
        self.current_sccm = 0.0

    @AbstractController.device_command()
    def set_target_sccm(self, sccm: float = 0.):
        sccm = min(200.0, max(0.0, sccm))
        assert 0.0 <= sccm <= 200.0
        self.target_sccm = sccm
        target_flow = sccm / 2.0

        if self.target_sccm <= 0.00001:  # TO CLOSE
            self.exec_command(register=REGISTER_SET_FLOW, value=0)
            self.exec_command(register=REGISTER_STATE_FLAGS_1, value=CLOSE_RRG_FLAGS)
            is_open = False
        else:
            """
            1. Set flow to target value (= sccm / 2)
            2. Open rrg
            """
            self.exec_command(register=REGISTER_SET_FLOW, value=target_flow)
            self.exec_command(register=REGISTER_STATE_FLAGS_1, value=OPEN_RRG_FLAGS)
            is_open = True

        self.is_open = is_open
        return self.is_open

    @AbstractController.device_command()
    def get_current_sccm(self):
        current_flow = self.exec_command(register=REGISTER_GET_FLOW)
        self.current_sccm = current_flow * 2.0
        return self.current_sccm