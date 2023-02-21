from threading import Thread
from time import sleep
from .constants import RECIPE_STATES

RECIPE_STATES_TO_STR = {
    RECIPE_STATES.RUN: "Running",
    RECIPE_STATES.PAUSE: "Pause",
    RECIPE_STATES.STOP: "Stop",
}

class RecipeRunner:
    def __init__(self,
                 set_current_recipe_step=None,  # set current action (index, name)
                 on_success_end_recipe=None,  # call at the end of all steps of recipe
                 on_error=None,  # add error
                 on_log=None,  # add log
                 ):
        self._recipe = None
        self._recipe_thread = None
        self._status = 0
        self._recipe_state = RECIPE_STATES.STOP

        self._on_success_end_recipe = on_success_end_recipe
        self._set_current_recipe_step = set_current_recipe_step

        # self.

    def _get_work_status(self):
        try:
            self._status = self.get_work_status()
        except:
            pass

    def set_recipe(self, recipe):
        self._recipe = recipe

    def check_recipe(self):
        """
        use on_log/on_error to say about problems with table
        :return: bool
        """
        return True

    def run_recipe(self):
        self._recipe_state = RECIPE_STATES.RUN
        for i in range(7):
            print(f"|>> START STEP {i} STATE:", RECIPE_STATES_TO_STR[self._recipe_state])
            if self._recipe_state == RECIPE_STATES.STOP:
                return

            while self._recipe_state == RECIPE_STATES.PAUSE:
                # print("IN PAUSE!")
                sleep(1)
            self._set_current_recipe_step(f"STEP:) [{i}]", i + 1)
            sleep(2)

        self._recipe_state = RECIPE_STATES.STOP
        self._on_success_end_recipe()

    @property
    def recipe_state(self):
        return self._recipe_state

    def set_recipe_state(self, state):
        # print("|> NEW RECIPE STATE:", state)
        if state == self._recipe_state or self._recipe_state == RECIPE_STATES.STOP:
            return
        self._recipe_state = state
