from ...system_actions import ManyDeviceSystemAction


class SingleAnswerSystemAction(ManyDeviceSystemAction):
    def _call_function(self, value, device_num=None):
        # print("CALL SIMPLE ANSWER SYS:", value, device_num)
        return value
