import time
from abc import abstractmethod

from .exceptions import NotAchievingActionGoal
from ..actions import Argument


class AppAction:
    args_info = []
    _args_amount = 0
    _args = []
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
        self.start_time = time.time()

    def _is_stop_state(self):
        if self.is_stop_state_function is not None:
            return self.is_stop_state_function()
        return False

    def _on_alert_interrupt(self):
        pass
        # self.system.add_error_log(f"Выполнение остановлено")

    def sub_action(self, action_class):
        sub_action = action_class()
        sub_action.system = self.system
        sub_action.is_stop_state_function = self.is_stop_state_function
        sub_action.is_pause_state_function = self.is_pause_state_function
        return sub_action

    def interrupt_if_stop_state(self):
        if self.is_stop_state_function is not None and self.is_stop_state_function() \
                and self.system is not None:
            self._on_alert_interrupt()
            raise NotAchievingActionGoal

    def _is_pause_state(self):
        if self.is_pause_state_function is not None:
            return self.is_pause_state_function()
        return False

    def _prepare_argument(self, arg, arg_class: Argument):
        # print("ARGS!", arg, arg_class)
        return arg_class.prepare_value(arg)

    def action(self, *args):
        assert len(args) == len(self.args_info), \
            f"Check correct arguments in {self.__class__.__name__}"
        self._args = args or []
        prepared_args = list(map(lambda x: self._prepare_argument(*x),
                                 zip(args, self.args_info)))

        self.start_time = time.time()
        self.do_action(*prepared_args)
        self.interrupt_if_stop_state()

    @abstractmethod
    def do_action(self, *args):
        pass

    @property
    def args_amount(self):
        if self._args_amount == 0:
            self._args_amount = len(self.args_info)
        return self._args_amount

    def check_args(self):
        return None

    def get_full_info_name(self, *args):
        # print('_args', self._args)
        name: str = self.name
        if (index := name.find('[')) >= 0:
            name = name[:index].strip()
        args = ', '.join(list(map(str, args))).strip()
        if args:
            args = f" [{args}]"
        return f"{name}{args}"
