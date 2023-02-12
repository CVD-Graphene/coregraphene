import uuid

from .constants import NOTIFICATIONS


class EventLog:
    def __init__(self, log, log_type=NOTIFICATIONS.LOG):
        self.uid = uuid.uuid4()
        self.log = log
        self.log_type = log_type

    def __str__(self):
        return f"{self.uid} | {self.log_type} | {self.log}"
