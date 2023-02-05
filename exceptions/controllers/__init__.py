import datetime


class BaseControllerException(Exception):
    def __init__(self, controller_id=None):
        self.controller_id = controller_id
        self.description = f"Controller raise exception"
        self.raised_at = datetime.datetime.now()

    def __str__(self):
        controller_str = "Controller"
        if self.controller_id:
            controller_str += f" id={self.controller_id}"
        return f"[ERROR {controller_str}] {self.raised_at} - {self.description}"


class ControllerInWaiting(BaseControllerException):
    def __init__(self, *args, left_seconds=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = f"Controller in waiting mode, left {left_seconds} s."


class SetupControllerException(BaseControllerException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = f"Controller setup error"
