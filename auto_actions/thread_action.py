from threading import Thread

from .actions_base import AppAction


class BaseThreadAction(object):
    _action_args = None

    def __init__(
            self,
            system=None,
            action=None,
    ):
        self.system = system
        self.action = action
        self._thread = None
        if self.action:
            self.action = action()
            self.action.system = self.system

    def set_action_args(self, *args):
        self._action_args = args

    def is_alive(self):
        return bool(self._thread and self._thread.is_alive())

    def join(self):
        if self._thread:
            self._thread.join()

    def start(self):
        try:
            self._thread = Thread(target=self.action.action, args=self._action_args or [])
            self._thread.start()
            # self.action.action(*self._action_args)
        except Exception as e:
            print("BaseThreadAction start error", e)
