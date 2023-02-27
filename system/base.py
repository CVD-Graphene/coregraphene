import os
import time
from abc import abstractmethod
from math import isnan

import pandas as pd
from threading import Thread

from .constants import NOTIFICATIONS
from .event_log import EventLog
from ..conf import settings
from ..exceptions.system import BaseConditionException
from ..components.controllers import AbstractController
from ..recipe import RECIPE_STATES, RecipeRunner

TABLE_COLUMN_NAMES = settings.TABLE_COLUMN_NAMES


class BaseSystem(object):
    """
    BaseSystem - class for managing controllers and saving device values

    Functions for implementing:
    1. _init_controllers - initialize and save controllers, use list `_controllers` for saving
    2. _init_values - initialize main values in system
    3. check_conditions - function raise BaseConditionException in case of
                        bad system state to prevent any action from user
    4. log_state - combine all values and save to log file
    5. _get_values - used for update reading values inside class
    """

    recipe_class = RecipeRunner

    def __init__(self, actions_list=None):
        self._last_action_answer = None
        self._errors = []
        self._event_logs = []
        self._is_working = True
        self._actions_list = actions_list

        self._recipe = None
        self._recipe_runner = self.recipe_class(
            # ...
            actions_list,
            system=self,
            on_end_recipe=self._on_end_recipe,
            set_current_recipe_step=self._set_current_recipe_step,
            on_error=self._add_error_log,
            on_log=self.add_log,
        )
        self._recipe_thread = None
        self._recipe_history = []
        self._recipe_current_step = ""
        self._recipe_state = RECIPE_STATES.STOP

        # CONTROLLERS
        self._controllers: list[AbstractController] = []

        self._determine_attributes()

        self._init_controllers()

        # VALUES
        self._init_values()

        self._init_actions()

        # self._add_error_log("Тупая тупая ошибка где много букв self.accurate_vakumetr_value = "
        #                     "self.accurate_vakume self.accurate_vakumetr_value = "
        #                     "self.accurate_vakumetr_controller.get_value()")
        # self._add_log("Тупая тупая заметка!!!!!", log_type=NOTIFICATIONS.LOG)

    def _determine_attributes(self):
        """
        Update ports, get values from system, etc
        :return:
        """
        pass

    @abstractmethod
    def _init_controllers(self):
        """
        Init controllers and save (!!!) them to `_controllers` list
        :return:
        """
        pass

    @abstractmethod
    def _init_actions(self):
        """
        Init auto_actions
        :return:
        """
        pass

    @abstractmethod
    def _init_values(self):
        pass

    @property
    def has_logs(self):
        return bool(self._event_logs)

    @property
    def first_log(self):
        try:
            return self._event_logs[0]
        except:
            return None

    def clear_log(self, uid):
        self._event_logs = list(filter(lambda x: x.uid != uid, self._event_logs))

    def setup(self):
        for controller in self._controllers:
            if controller is not None:
                controller.setup()

    def threads_setup(self):
        """
        Set `_thread_using` to True for controllers to activate thread_setup and thread running
        :return:
        """
        for controller in self._controllers:
            if controller is not None:
                controller.thread_setup(
                    self.is_working,
                    self._add_log,
                    self._add_error_log
                )
                controller.run()

        self._recipe_thread = Thread(target=self._recipe_runner.thread_run)
        self._recipe_thread.start()

    def stop(self):
        """
        Function for execute before closing main ui program to destroy all threads
        :return:
        """
        self._is_working = False

    def is_working(self):
        return self._is_working

    def destructor(self):
        print("System del | Controllers:", len(self._controllers))
        self._is_working = False
        for controller in self._controllers:
            if controller is not None:
                controller.destructor()
        if self._recipe_thread is not None:
            try:
                self.on_stop_recipe()
                self._recipe_thread.join()
            except Exception as e:
                print("Join recipe thread error:", e)

    @abstractmethod
    def check_conditions(self):
        """
        Raise condition exception if one of conditions is not correct
        :return: True or raise exception from BaseConditionException
        """
        return True

    def action(func):
        """
        Decorator for auto_actions, that check all conditions and system state
        :return: new decorated function
        """

        def wrapper(self, *args, **kwargs):
            try:
                self.check_conditions()

                answer = func(self, *args, **kwargs)
                self._last_action_answer = answer
                return answer
            except Exception as e:
                return self._handle_exception(e)

        return wrapper

    def _add_log(self, log, log_type=NOTIFICATIONS.LOG):
        try:
            self._event_logs.append(EventLog(log, log_type=log_type))
        except Exception as e:
            print(f"Add event log error: {e}")

    def _add_error_log(self, e):
        self._add_log(str(e), log_type=NOTIFICATIONS.ERROR)

    def add_error_log(self, e):
        self._add_log(str(e), log_type=NOTIFICATIONS.ERROR)

    def add_log(self, log):
        self._add_log(log)

    def add_error(self, e):
        self._add_error_log(e)

    def _handle_exception(self, e):
        print(f"Raise exception in handler!::, {self.__class__.__name__}", e)
        self._add_error_log(e)
        self._errors.append(e)
        if isinstance(e, BaseConditionException):
            pass

    @abstractmethod
    def log_state(self):
        """
        Save current values to log file
        """
        pass

    def get_values(self):
        """
        Use this function for update reading values.
        It's called constantly for getting actual values.
        :return:
        """
        try:
            self._get_values()
        except Exception as e:
            self._add_error_log(e)

    @abstractmethod
    def _get_values(self):
        """
        Override this for getting values from controllers and save them locally
        """
        pass

    @property
    def recipe_state(self):
        return self._recipe_runner.recipe_state

    def get_recipe_state(self):
        return self.recipe_state

    def on_pause_recipe(self):
        new_state = RECIPE_STATES.PAUSE if self.recipe_state == RECIPE_STATES.RUN else \
            RECIPE_STATES.RUN
        print("AFTER ON PAUSE: NEW STATE:", new_state)
        self._recipe_runner.set_recipe_state(new_state)

    def on_stop_recipe(self):
        self._recipe_runner.set_recipe_state(RECIPE_STATES.STOP)

    def save_recipe_file(self, path: str = None, file: str = None, file_path=None, data=None):
        if file_path is None and (file is None or len(file) < 8):
            self._handle_exception(Exception(f"Ошибка сохранения {file}: название файла не может быть меньше 8 символов"))
            return
        try:
            df = pd.DataFrame(data, columns=TABLE_COLUMN_NAMES)
            total_path = file_path if file_path else os.path.join(path, file)  # "recipes/test3.xlsx"
            df.to_excel(excel_writer=total_path)
        except Exception as e:
            self._handle_exception(Exception(f"Ошибка сохранения {file}: {str(e)}"))
        else:
            self._add_log(f"Файл {file} сохранён")

    def get_recipe_file_data(self, file_path: str):
        file_name = None
        try:
            file_name = os.path.basename(file_path)
            # print("FILE P:", file_path, file_name)
            excel_data_df = pd.read_excel(file_path, header=None)
            cols = excel_data_df.columns.ravel()
            arr = []
            for col in cols[1:]:
                a = excel_data_df[col].tolist()[1:]
                for i in range(len(a)):
                    # try:
                    if i + 1 > len(arr):
                        arr.append([])
                    if type(a[i]) != str and isnan(a[i]):
                        a[i] = ""
                    arr[i].append(str(a[i]))
            # print("RECIPE GET ARRAY DATA", arr)
            return arr
        except Exception as e:
            self._handle_exception(Exception(f"Ошибка открытия {file_name}: {str(e)}"))

    def _on_end_recipe(self, success=False):
        try:
            if success:
                self._add_log("Рецепт успешно выполнен")
            else:
                pass
            # self._recipe_thread.join()
            # self._recipe_thread = None
            self._recipe = None
            print("AFTER ALL END!")
            time.sleep(2)
        except Exception as e:
            print("On end recipe error:", e)

    def set_recipe(self, recipe):
        self._recipe = recipe
        self._recipe_runner.set_recipe(self._recipe)

    def check_recipe_is_correct(self):
        ready = self._recipe_runner.check_recipe()
        return ready

    def run_recipe(self):
        self._recipe_history = []
        # if type(recipe) != list:
        #     self._add_error_log(Exception("Чтение рецепта завершилось с ошибками"))
        #     return False

        # self._recipe = recipe
        # self._recipe_runner.set_recipe(self._recipe)
        self._recipe_runner.start_recipe()
        # ready = self._recipe_runner.check_recipe()
        # if ready:
        #     self._recipe_thread = Thread(target=self._recipe_runner.run_recipe)
        #     self._recipe_thread.start()
        # print("|>> WHAT'S READY:", ready)
        # return ready

    def _set_current_recipe_step(self, name, index=None):
        index = index if index else (len(self._recipe_history) + 1)
        self._recipe_current_step = {'name': name, 'index': index}
        self._recipe_history.append(self._recipe_current_step)

    @property
    def current_recipe_step(self):
        return self._recipe_current_step
