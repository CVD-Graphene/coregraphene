from .base import AbstractController
from ..devices import ValveDevice

CLOSE = 1
OPEN = 0


class ValveController(AbstractController):
    def __init__(self, port):
        super().__init__()
        self.device = ValveDevice(
            port=port,
            default_command=CLOSE,
        )
        self.is_open = False

    def _send_command(self, command):
        answer = self.exec_command(command=command)
        self.is_open = not bool(answer)
        return answer

    @AbstractController.device_command()
    def change_state(self):
        """Return if valve is open"""
        command = CLOSE if self.is_open else OPEN
        return self._send_command(command)

    @AbstractController.device_command()
    def open(self):
        return self._send_command(OPEN)

    @AbstractController.device_command()
    def close(self):
        return self._send_command(CLOSE)
