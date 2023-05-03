import time
from threading import Thread

from .actions_base import AppAction


class BaseBackgroundAction(object):
    """
    The main purpose of creating this class is to simulate the behavior
    of a real microcontroller for a device or multiple devices
    that perform specific tasks on a continuous basis.

    For example, a controller to hold pressure at a desired level by adjusting a valve.
    Such actions are required to be performed in the background
    on a constant basis based on system commands.
    """

    _action_args = None
    _active = False
    action_class: AppAction = None

    is_stop_state_function = None
    is_pause_state_function = None

    def __init__(
            self,
            system=None,
            action=None,
    ):
        self.system = system
        self._thread = None
        if action:
            self.action = action
        elif self.action_class:
            self.action = self.action_class()

    def set_action_args(self, *args):
        self._action_args = args

    def get_action_args(self):
        return self._action_args or []

    def is_alive(self):
        return bool(self._thread and self._thread.is_alive())

    def join(self):
        if self._thread:
            self._thread.join()
            self._thread = None

    # def activate(self):
    #     self._active = True

    def is_active(self):
        return self._active

    def _is_stop_state_function(self):
        if self.is_stop_state_function:
            return self.is_stop_state_function()
        return True

    def run(self):
        self._thread = Thread(target=self._run)
        self._thread.start()

    def _run(self):
        while self.system.is_working():
            time.sleep(1)
            if self._is_stop_state_function():
                continue

            try:
                self.action.is_stop_state_function = self.is_stop_state_function
                self.action.is_pause_state_function = self.is_pause_state_function
                self.action.system = self.system
                self.action.action(*self.get_action_args())
            except Exception as e:
                print("ERROR _run BaseBackgroundAction:", e)
            self._active = False
