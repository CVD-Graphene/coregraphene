import asyncio
import os
import time
from abc import abstractmethod
from math import isnan

import pandas as pd
from threading import Thread

from .constants import NOTIFICATIONS
from .event_log import EventLog
from ..auto_actions import BaseThreadAction
from ..conf import settings
from ..exceptions.system import BaseConditionException
from ..components.controllers import AbstractController
from ..recipe import RECIPE_STATES, RecipeRunner
from ..system_actions import SetCurrentRecipeStepAction, BaseSignalAction
from ..utils import get_available_usb_ports

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

        self.ports = {}
        self._controllers_check_classes = {}
        self._ports_attr_names = {}
        self._default_controllers_kwargs = {}

        self._recipe = None
        self._recipe_runner = self.recipe_class(
            # ...
            actions_list,
            system=self,
            on_end_recipe=self._on_end_recipe,
            set_current_recipe_step=self.set_current_recipe_step,
            on_error=self._add_error_log,
            on_log=self.add_log,
        )
        self._recipe_thread = None
        self._recipe_history = []
        self._recipe_current_step = ""
        self._recipe_state = RECIPE_STATES.STOP

        self._actions_thread = None
        self._active_actions_array = []
        self._history_actions_array = []
        self._potential_actions_array = []
        self._background_actions_array = []

        self._system_actions_array = []
        self._system_actions_callbacks_thread = None

        # CONTROLLERS
        self._controllers: list[AbstractController] = []

        self._determine_attributes()

        self._init_controllers()

        # VALUES
        self._init_values()

        self._init_actions()

        self._init_background_actions()

        self._collect_actions()

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

    def get_potential_controller_port(self, controller_port, controller_code):
        new_port = controller_port
        try:
            used_ports = [value for key, value in self.ports.items() if key != controller_code]
            usb_ports = get_available_usb_ports()
            for used_port in used_ports:
                try:
                    usb_ports.remove(used_port)
                except:
                    continue

            controller_check_class = self._controllers_check_classes[controller_code]
            for port in usb_ports:
                controller: AbstractController = controller_check_class(
                    port=port,
                    **self._default_controllers_kwargs.get(controller_code, {})
                )
                controller.setup()

                if controller.check_command():
                    new_port = port
                    setattr(self, self._ports_attr_names[controller_code], new_port)
                    self.ports[controller_code] = new_port

                    controller.destructor()
                    del controller
                    break

                controller.destructor()
                del controller

            # new_port = usb_ports[0]
            # setattr(self, self._ports_attr_names[controller_code], new_port)
            # self.ports[controller_code] = new_port
        except Exception as e:
            print("|<<< NEW PORT GET ERROR:", e)

        print(f"\n|>>> NEW PORT FOR {controller_code}: {new_port}\n")
        return new_port

    @abstractmethod
    def _init_controllers(self):
        """
        Init controllers and save (!!!) them to `_controllers` list
        :return:
        """
        pass

    def _init_background_actions(self):
        pass

    def _init_actions(self):
        """
        Init auto_actions
        :return:
        """
        self.set_current_recipe_step_action = SetCurrentRecipeStepAction(system=self)

    def _collect_actions(self):
        # method_list = []

        # attribute is a string representing the attribute name
        for attribute in dir(self):
            # Get the attribute value
            attribute_value = getattr(self, attribute)
            # Check that it is callable
            if callable(attribute_value) and isinstance(
                attribute_value, BaseSignalAction
            ):
                # Filter all dunder (__ prefix) methods
                if not attribute.startswith('__'):
                    self._system_actions_array.append(attribute_value)

        # print("_system_actions_array:", self._system_actions_array)

    def _system_actions_callbacks_loop(self):
        while self.is_working():
            time.sleep(0.3)
            for system_action in self._system_actions_array:
                try:
                    system_action.send_delayed_callbacks()
                except Exception as e:
                    print("_system_actions_callbacks_loop error:", e)

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

        # for action in self._background_actions_array:
        #     action.run()

        self._actions_thread = Thread(target=self._run_actions_loop)
        self._actions_thread.start()

        self._system_actions_callbacks_thread = Thread(
            target=self._system_actions_callbacks_loop
        )
        self._system_actions_callbacks_thread.start()

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
        if self._actions_thread is not None:
            try:
                self._actions_thread.join()
            except Exception as e:
                print("Join recipe thread error:", e)

        self._system_actions_callbacks_thread.join()

        for action in self._potential_actions_array:
            action.join()

        for action in self._background_actions_array:
            action.join()

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
            # print("MEMORY SYSTEM:", deep_getsizeof(self, set()))
            self._get_values()
        except Exception as e:
            self._add_error_log(e)

    def _run_actions_loop(self):
        while self.is_working() or self._active_actions_array:
            try:

                # pop_indexes = []
                # for i, action in enumerate(self._active_actions_array):
                #     # print("AUAU", i, thread)
                #     if not action.is_alive():  # Fix for working on raspberry PI
                #         # action.join()
                #         pop_indexes.append(i)
                #         print("ACTION THREAD JOINED!")
                #         self._history_actions_array.append(action)
                #
                # self._active_actions_array = list(
                #     map(
                #         lambda x: x[1],
                #         filter(lambda x: x[0] not in pop_indexes, enumerate(self._active_actions_array))
                #         )
                # )
                # print("ACT ARR LEN:", len(self._active_actions_array))

                for action in self._potential_actions_array:
                    if not action.is_active():
                        action.start()

                # if len(self._potential_actions_array) > 0 and self.is_working():
                #     # print("IN POTENTIAL ARR:", len(self._potential_actions_array))
                #     action: BaseThreadAction = self._potential_actions_array[0]
                #     action.start()
                #     # thread = Thread(target=action.run)
                #     # thread.start()
                #     self._potential_actions_array.pop(0)
                #     self._active_actions_array.append(action)

                time.sleep(1)

            except Exception as e:
                print("_run_actions_loop error:", e)

    def _add_action_to_loop(self, thread_action: BaseThreadAction):
        # thread_action.start()
        self._potential_actions_array.append(thread_action)

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

    def set_current_recipe_step(self, name, index=None):
        return self.set_current_recipe_step_action(name, index=index)

    def _set_current_recipe_step(self, name, index=None):
        index = index if index else (len(self._recipe_history) + 1)
        self._recipe_current_step = {'name': name, 'index': index}
        self._recipe_history.append(self._recipe_current_step)

        return self._recipe_current_step

    @property
    def current_recipe_step(self):
        return self._recipe_current_step

    @property
    def last_recipe_steps(self):
        return reversed(self._recipe_history[-2:])
