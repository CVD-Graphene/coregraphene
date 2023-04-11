import uuid
from abc import abstractmethod
from threading import Lock


class ConnectFunction:
    func = None
    uid = None

    def __init__(self, func, **kwargs):
        self.uid = uuid.uuid4()
        self.func = func
        self.filter_kwargs = kwargs


class BaseSignalAction(object):

    def __init__(self, *args, **kwargs):
        self._callback_array = []
        self._last_values = None

        self._lock = Lock()
        # self._

    def _pre_call(self, *args, **kwargs):
        pass

    def _on_get_value(self, value):
        pass

    def _update_value_for_functions(self, value):
        if type(value) == set:
            value = list(value)
        if type(value) not in [list, ]:
            value = [value]
        return value

    @property
    def _additional_kwargs_to_func(self):
        return {}

    def __call__(self, *args, **kwargs):
        try:
            self._pre_call(*args, **kwargs)

            value = self._call_function(*args, **kwargs)
            self._on_get_value(value)

            value = self._update_value_for_functions(value)

            changed_answer = self._check_answer_changed(value)

            if changed_answer:
                filtered_array = self._filter_callback_array(*args, **kwargs)
                for connect_func in filtered_array:
                    connect_func.func(*value, **self._additional_kwargs_to_func)

            return value
        except Exception as e:
            return self._handle_exception(e)

    @abstractmethod
    def _handle_exception(self, e: Exception):
        raise e

    def _check_answer_changed(self, new_answer):
        return True
        # if self._last_values is None or len(self._last_values) != len(new_answer):
        #     self._last_values = new_answer
        #     return True
        # for a, b in zip(self._last_values, new_answer):
        #     if a != b:
        #         self._last_values = new_answer
        #         return True
        # return False

    def _filter_callback_array(self, *args, **kwargs):
        return self._callback_array

    @abstractmethod
    def _call_function(self, *args, **kwargs):
        pass

    def connect(self, func, **kwargs):
        connect_func = ConnectFunction(func, **kwargs)
        self._callback_array.append(connect_func)
        return connect_func.uid

    def unsubscribe(self, uid):
        self._callback_array = list(
            filter(lambda x: x.uid != uid, self._callback_array))


class SystemAction(BaseSignalAction):
    def __init__(self, system, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._system = system

    def _pre_call(self, *args, **kwargs):
        self._system.check_conditions()

    def _on_get_value(self, value):
        self._system._last_action_answer = value

    def _handle_exception(self, e: Exception):
        return self._system._handle_exception(e)


# class ManyDeviceSignalAction(BaseSignalAction):
#     def _filter_callback_array(self, *args, device_num=None, **kwargs):
#         def check_device(connect_function):
#             _device_num = connect_function.filter_kwargs.get('device_num', None)
#             # print('Dev num::', _device_num, device_num)
#             return _device_num == device_num or _device_num is None
#
#         arr = list(filter(check_device, self._callback_array))
#         # print("CHECK ARGS:", device_num, kwargs, args, self._callback_array)
#         # print("SORTED ARR ACTION", arr)
#         return arr


class ManyDeviceSystemAction(SystemAction):
    # pass
    def _filter_callback_array(self, *args, device_num=None, **kwargs):
        def check_device(connect_function):
            _device_num = connect_function.filter_kwargs.get('device_num', None)
            # print('Dev num::', _device_num, device_num)
            return _device_num == device_num or _device_num is None

        arr = list(filter(check_device, self._callback_array))
        # print("CHECK ARGS:", device_num, kwargs, args, self._callback_array)
        # print("SORTED ARR ACTION", arr)
        return arr


class ControllerAction(BaseSignalAction):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controller = controller

    # def __call__(self, *args, **kwargs):
    #     print("Call @@@", args, kwargs)

    def _handle_exception(self, e: Exception):
        print("ERROR ACTION CONTROLLER", e)
        return self._controller._add_error(e)

    def current_device_num(self):
        return self._controller._last_thread_command.device_num

    @property
    def _additional_kwargs_to_func(self):
        return {'device_num': self.current_device_num()}

    # def _update_value_for_functions(self, value):
    #     value = super()._update_value_for_functions(value)
    #     value.append(self.current_device_num())
    #     return value


class ManyDeviceControllerAction(ControllerAction):
    def _filter_callback_array(self, *args, **kwargs):
        device_num = self.current_device_num()

        def check_device(connect_function):
            _device_num = connect_function.filter_kwargs.get('device_num', None)
            # print('Dev num::', _device_num, device_num)
            return _device_num == device_num or _device_num is None

        arr = list(filter(check_device, self._callback_array))
        # print("CHECK ARGS:", device_num, kwargs, args, self._callback_array)
        # print("SORTED ARR ACTION", arr)
        return arr
