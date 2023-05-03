from ...system_effects import ManyDeviceSystemEffect


class SingleAnswerSystemEffect(ManyDeviceSystemEffect):
    def _call_function(self, value, device_num=None):
        # print("CALL SIMPLE ANSWER SYS:", value, device_num)
        return value
