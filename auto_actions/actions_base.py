from abc import abstractmethod


class AppAction:
    args_info = []
    _args_amount = 0
    key = None
    name = None
    system = None
    is_stop_state_function = None
    is_pause_state_function = None

    # def __init__(self, name: str = None, key: str = None, args_info: list = None):
    #     self.name = name
    #     self.key = key
    #     self.args_info = args_info or []
    #     self.args_amount = len(self.args_info)

    def __init__(self):
        self._args_amount = len(self.args_info)

    def _is_stop_state(self):
        if self.is_stop_state_function is not None:
            return self.is_stop_state_function()
        return False

    def _is_pause_state(self):
        if self.is_pause_state_function is not None:
            return self.is_pause_state_function()
        return False

    # def set_functions(self,
    #                   system=None,
    #                   **kwargs):
    #     self.system = system

    @abstractmethod
    def action(self, *args, **kwargs):
        pass

    @property
    def args_amount(self):
        if self._args_amount == 0:
            self._args_amount = len(self.args_info)
        return self._args_amount

    def check_args(self):
        return None
