import uuid
from abc import abstractmethod


class ConnectFunction:
    func = None
    uid = None

    def __init__(self, func):
        self.uid = uuid.uuid4()
        self.func = func


class SystemAction(object):

    def __init__(self, system):
        self._system = system
        self._callback_array = []

    def __call__(self, *args, **kwargs):
        try:
            self._system.check_conditions()

            value = self._call_function(*args, **kwargs)
            self._system._last_action_answer = value

            if type(value) != list:
                value = [value]

            for connect_func in self._callback_array:
                connect_func.func(*value)

            return value
        except Exception as e:
            return self._system._handle_exception(e)

    @abstractmethod
    def _call_function(self, *args, **kwargs):
        pass

    def connect(self, func):
        connect_func = ConnectFunction(func)
        self._callback_array.append(connect_func)
        return connect_func.uid

    def unsubscribe(self, uid):
        self._callback_array = list(
            filter(lambda x: x.uid != uid, self._callback_array))
