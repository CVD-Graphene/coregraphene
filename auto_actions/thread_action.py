from .actions_base import AppAction


class BaseThreadAction(object):
    action: AppAction = None
    _action_args = None

    def __init__(
            self,
            system=None,
            action=None,
    ):
        self.system = system
        self.action = action or self.action
        if self.action:
            self.action = action()
            self.action.system = self.system

    def set_action_args(self, *args):
        self._action_args = args

    def run(self):
        try:
            self.action.action(*self._action_args)
        except Exception as e:
            print("BaseThreadAction run error", e)
