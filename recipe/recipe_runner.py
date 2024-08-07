from abc import abstractmethod

from coregraphene.utils.actions import get_action_by_name
from coregraphene.actions import AppAction, Argument
from time import sleep
from .constants import RECIPE_STATES
from ..actions.exceptions import NotAchievingActionGoal
from ..exceptions import BaseConditionException

RECIPE_STATES_TO_STR = {
    RECIPE_STATES.RUN: "Running",
    RECIPE_STATES.PAUSE: "Pause",
    RECIPE_STATES.STOP: "Stop",
}


class RecipeRunner:
    def __init__(self,
                 actions_list,
                 system=None,
                 # set_recipe_step=None,
                 set_current_recipe_step=None,  # set current action (index, name)
                 on_end_recipe=None,  # call at the end of all steps of recipe
                 on_error=None,  # add error
                 on_log=None,  # add log
                 ):
        self._system = system
        self._actions_list = actions_list
        self._recipe = None
        self._recipe_thread = None
        self._status = 0
        self._recipe_state = RECIPE_STATES.STOP

        self._on_end_recipe = on_end_recipe
        self._set_current_recipe_step = set_current_recipe_step
        self._on_error = on_error
        self._on_log = on_log

    def set_recipe(self, recipe):
        self._recipe = recipe

    def start_recipe(self):
        self._recipe_state = RECIPE_STATES.RUN

    def _is_stop_recipe(self):
        return self.get_current_recipe_state() == RECIPE_STATES.STOP

    def _is_pause_recipe(self):
        return self.get_current_recipe_state() == RECIPE_STATES.PAUSE

    def thread_run(self):
        while self._system.is_working():
            sleep(1)
            if self._recipe_state == RECIPE_STATES.STOP:
                continue
            if self._recipe_state == RECIPE_STATES.RUN:
                self.run_recipe()
                self._recipe_state = RECIPE_STATES.STOP
        sleep(1)

    def get_current_recipe_state(self):
        return self._recipe_state

    def check_recipe(self):
        """
        use on_log/on_error to say about problems with table
        :return: bool
        """
        # print("RECIPE:")
        for action_index, action in enumerate(self._recipe):
            if len(action) == 0:
                continue
            line_number = action_index + 1
            str_line_num = f"(строка {line_number})"
            action_table_name = action[0]
            action_obj, index = get_action_by_name(action_table_name, self._actions_list)
            action_obj: AppAction = action_obj
            if action_obj is None:
                self._on_error(f"Действие `{action_table_name}` не реализовано в программе {str_line_num}")
                return False
            if (args_amount := action_obj.args_amount) > 0:
                args = action[1:1 + args_amount]
                for i, arg in enumerate(args):
                    checker: Argument = action_obj.args_info[i]()
                    # print("Checker:", checker, arg)
                    check_str = checker.check(arg)
                    # print("CHECK STR:", check_str)
                    if check_str:
                        self._on_error(
                            f"Действие `{action_table_name}`: аргумент №{i + 1} - {check_str} {str_line_num}"
                        )
                        return False
            # print(action)
        return True

    def run_recipe(self):
        actions_array = []

        for action_index, action in enumerate(self._recipe):
            try:
                if len(action) == 0:
                    continue

                action_table_name = action[0]
                action_obj, index = get_action_by_name(action_table_name, self._actions_list)
                actions_array.append([action_obj, action[1:1 + action_obj.args_amount]])

                # args = action[1:1 + action_obj.args_amount]
                # action_obj.action(*args)

            except Exception as e:
                print("Error preparation recipe run:", e)
                return

        self.run_recipe_actions(actions_array)

    def run_recipe_actions(self, actions: list):
        success = True
        sleep(0.5)
        for action_index, (action_obj, action_args) in enumerate(actions):
            try:
                if self._recipe_state == RECIPE_STATES.STOP:
                    self._system.add_error(f"Принудительное завершение рецепта.")
                    return

                while self._recipe_state == RECIPE_STATES.PAUSE:
                    sleep(1)

                action_obj: AppAction = action_obj

                # self._set_current_recipe_step(f"ШАГ №{action_index + 1}: {action_table_name}")
                self._set_current_recipe_step(f"{action_obj.get_full_info_name(*action_args)}")

                action_obj.system = self._system
                action_obj.is_stop_state_function = self._is_stop_recipe
                action_obj.is_pause_state_function = self._is_pause_recipe
                action_obj.action(*action_args)

            except (NotAchievingActionGoal, BaseConditionException) as e:
                self._system.add_error(f"Цель шага №{action_index + 1} не достигнута. "
                                       f"Завершение рецепта.")
                self._on_not_achieving_recipe_step_action()
                success = False
                break
        # print("DONE!")
        sleep(1)
        self._recipe_state = RECIPE_STATES.STOP
        self._on_end_recipe(success=success)
        # print("AFTER END!")

    @abstractmethod
    def _on_not_achieving_recipe_step_action(self):
        pass

    @property
    def recipe_state(self):
        return self._recipe_state

    def set_recipe_state(self, state):
        # print("|> NEW RECIPE STATE:", state)
        if state == self._recipe_state or self._recipe_state == RECIPE_STATES.STOP:
            return
        self._recipe_state = state
