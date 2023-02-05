from .base import AbstractController
from components.devices import ValveDevice

CLOSE = 1
OPEN = 0


class ValveController(AbstractController):
    def __init__(self, port):
        super().__init__()
        self.device = ValveDevice(port=port)
        self.is_open = False

    @AbstractController.device_command()
    def change_state(self):
        """Return if valve is open"""
        command = CLOSE if self.is_open else OPEN
        answer = self.exec_command(command=command)
        # print(f"command {command}, answer {answer}")
        self.is_open = not bool(answer)
        return answer
