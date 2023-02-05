import datetime


class BaseDeviceException(Exception):
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.description = f"Device raise exception"
        self.raised_at = datetime.datetime.now()

    def __str__(self):
        device_str = "Device"
        if self.device_id:
            device_str += f" id={self.device_id}"
        return f"[ERROR {device_str}] {self.raised_at} - {self.description}"


class DefectiveDeviceException(BaseDeviceException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = f"Defective device"


class InactiveDeviceException(BaseDeviceException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = f"Device was not activate"


class SetupDeviceException(BaseDeviceException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = f"Device setup error"


class DoubleDeclarationCommunicatorException(BaseDeviceException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.description = f"Use the only one of: or __init__ arg `communicator` " \
                           f"or property `communicator_class`. " \
                           f"The last one is used only without any initialization."
