import datetime


class BaseCommunicationMethodException(Exception):
    def __init__(self, communication_method_id=None):
        self.communication_method_id = communication_method_id
        self.description = f"Method raise exception"
        self.raised_at = datetime.datetime.now()

    def __str__(self):
        communication_method_str = "CommunicationMethod"
        if self.communication_method_id:
            communication_method_str += f" id={self.communication_method_id}"
        return f"[ERROR {communication_method_str}] {self.raised_at} - {self.description}"


class CommunicationMethodNotSetup(BaseCommunicationMethodException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = f"Communication method not setup. Call `setup()` before using."


# class SetupControllerException(BaseControllerException):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.description = f"Controller setup error"
