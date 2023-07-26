import datetime
import time
import asyncio
import traceback
from abc import abstractmethod
from threading import Thread

from ..commands import BaseCommand
from ..devices import AbstractDevice
from ...exceptions.controllers import ControllerInWaiting
from ...conf import settings


class AbstractController(object):
    """
    Class for device controllers
    """

    device_class = None
    code = None  # str controller code
    MAX_NUMBER_COMMAND_ATTEMPTS = 5
    works_correctly = True

    logs_parameters = None

    def __init__(self, *args, active=True, **kwargs):
        self._active = active

        if self.device_class is not None and self._active:
            self.device: AbstractDevice = self.device_class(
                *args, **kwargs
            )
        else:
            self.device = None

        self.controller_id = self.__class__.__name__
        self.loop_delay = 0.2

        # THREAD VARIABLES ############################
        # if True - system will run thread_setup
        self._thread_using = False

        self._runnable = False
        self._is_global_working = True
        self._thread = None
        self._commands_queue = []
        self._is_thread_reading = False
        self._last_thread_command: BaseCommand = None
        self._start_thread_read_time = None
        self._critical_read_time = 3.0  # -0.1 if settings.LOCAL_MODE else 3.0

        # target value and function for calling after sensor reach this value
        self._target_value = None
        self._on_reached = None

        # Params for setting sensor unreachable for time of delay
        self._start_timer = None
        self._delay = None
        self._after_waiting = None

        self._last_answer = None
        self._errors = []

        self._add_log = None
        self._add_error = None

    def thread_setup(self, is_working, add_log, add_error, **kwargs):
        """
        Set `_thread_using` to True for auto calling thread_setup
        :param is_working:
        :param add_log:
        :param add_error:
        :param kwargs:
        :return:
        """
        if not self._thread_using or not self._active:
            return
        self._runnable = True
        self._is_global_working = is_working
        self._add_log = add_log
        self._add_error = add_error
        self._thread_setup_additional(**kwargs)

    @abstractmethod
    def _thread_setup_additional(self, **kwargs):
        pass

    def check_command(self, **kwargs):
        """
        Check that all setup params are correct
        :return: True if correct, else False
        """
        try:
            self._check_command(**kwargs)
            return True
        except:
            return False

    def _check_command(self, **kwargs):
        """
        Use this function for check all params for devices
        :return: True/False
        """
        return True

    @property
    def _is_working(self):
        if type(self._is_global_working) == bool:
            return self._is_global_working
        return self._is_global_working()

    def set_logs_parameters_array(self):
        if self.logs_parameters is None:
            logs_parameters = self._set_logs_parameters_array()
            if logs_parameters is not None:
                self.logs_parameters = logs_parameters

    def _set_logs_parameters_array(self):
        return []

    def get_log_values(self):
        values = self._get_log_values()

        for name in values.keys():
            assert name in self.logs_parameters, \
                f'Parameter {name} not in logs_parameters list in {self.__class__.__name__}'

        return values

    def _get_log_values(self):
        return {}

    def _on_thread_error(self, exception: Exception):
        self._add_error(exception)

    def add_command(self, command: BaseCommand):
        if self._runnable and self._is_working:
            self._commands_queue.append(command)

    def _add_command_force(self, command: BaseCommand):
        if self._runnable:
            self._commands_queue.insert(0, command)

    def _run_thread_command(self, command: BaseCommand):
        self._last_thread_command = command
        self._exec_command(command=command)
        if command.on_completed:
            command.on_completed()

    def _thread_read_command(self):
        # print("1111")
        if self._start_thread_read_time is None:
            self._start_thread_read_time = time.time()

        if time.time() - self._start_thread_read_time > self._critical_read_time:
            # print("2222")
            self._start_thread_read_time = None
            self._is_thread_reading = False
            read_value = ""
            self._on_thread_error(Exception(
                f"{self.controller_id}: Прибор не отвечает дольше критического времени: "
                f"> {self._critical_read_time} сек."))
        else:
            # print("3333")
            read_value = self.read(**self._last_thread_command.kwargs)
            # print("4444,", read_value)
            # com_name = self._last_thread_command.kwargs.get("command", "SMTH")
            # print(f"|> [Controller thread {self.__class__.__name__}] "
            #       f"Read [command={com_name}]: value={read_value}.")
            if read_value is not None and not\
                    (type(read_value) == str and len(read_value) == 0):
                self._start_thread_read_time = None
                self._is_thread_reading = False
                # print("READ FOR:", self._last_thread_command.command)
                self._last_thread_command.on_answer(read_value)
        return read_value

    def _run(self):
        """
        Main loop for running commands from self._commands_queue
        :return: None
        """
        if not self._active:
            return

        to_exit = False
        attempts = 0
        # with_error = False
        counter = 0
        while True:
            # if counter % 25 == 0:
            #     print("COMMANDS:", len(self._commands_queue))
            # counter += 1
            # time.sleep(self.loop_delay)
            if self.loop_delay is not None and self.loop_delay > 0.0:
                time.sleep(self.loop_delay)
            try:
                if self._is_thread_reading:
                    self._thread_read_command()
                elif len(self._commands_queue) > 0:
                    if not self._is_working and not to_exit:
                        self._commands_queue.clear()
                        continue
                    command: BaseCommand = self._commands_queue.pop(0)
                    self._last_thread_command = command
                    # print("|> CURRENT COMMAND [c]:", command.command)

                    if command.with_answer:
                        self._is_thread_reading = True

                    if command.immediate_answer:
                        self._thread_read_command()
                        # command.on_answer(answer)
                    else:
                        self._run_thread_command(command)

                    # Must be the last to avoid duplicates because of errors
                    if command.repeat:
                        self._commands_queue.append(command)

                else:
                    if to_exit:
                        break
                    if not self._is_working:
                        to_exit = True
                        self._commands_queue = self._get_last_commands_to_exit()

                # with_error = False
                attempts = 0
                self.works_correctly = True
            except Exception as e:
                # with_error = True
                self.works_correctly = False
                try:
                    print(f"[{datetime.datetime.now().replace(microsecond=0)}] "
                          f"ERROR DURING EXECUTING COMMAND:", str(e))
                except Exception as pe:
                    print("ERROR PRINTING CONTROLLER RUN EXCEPTION :(")
                attempts += 1
                # if attempts < self.MAX_NUMBER_COMMAND_ATTEMPTS:
                #     self._add_command_force(self._last_thread_command)
                if attempts >= self.MAX_NUMBER_COMMAND_ATTEMPTS:
                    attempts = 0
                    self._reinitialize_communication()
                    self._on_thread_error(e)
                if self._is_working:
                    self._add_command_force(self._last_thread_command)

    def run(self):
        if self._runnable and self._thread is None and self._active:
            self._thread = Thread(target=self._run)
            self._thread.start()

    def _reinitialize_communication(self):
        pass

    def _get_last_commands_to_exit(self):
        return []

    def setup(self):
        if not self._active:
            return
        self.device.setup()

    def destructor(self):
        if not self._active:
            return

        if self._thread is not None:
            self._thread.join()
        self.device.destructor()

    @property
    def is_get_value(self):
        return True

    def device_command(strong=False):
        """
        Decorator for commands
        :return: new decorated function
        """
        def command_wrapper(func):
            def wrapper(self, *args, **kwargs):
                try:
                    if not strong and not self._active:
                        raise ControllerInWaiting(controller_id=self.controller_id)
                    self._last_answer = func(self, *args, **kwargs)
                    return self._last_answer
                except Exception as e:
                    return self._handle_exception(e)

            return wrapper
        return command_wrapper

    def thread_command(func):
        """
        Decorator for commands
        :return: new decorated function
        """
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                return self._on_thread_error(e)

        return wrapper

    @device_command()
    def exec_command(self, **kwargs):
        """
        Send command with value to sensor
        :param command:
        :param value:
        :return: answered value from sensor
        """
        return self.device.exec_command(**kwargs)

    @device_command()
    def _exec_command(self, command: BaseCommand):
        """
        Send command with value to sensor
        :param command: BaseCommand obj
        :return: answered value from sensor
        """
        return self.device.exec_command(
            **command.kwargs,
            # command=command.command,
            # value=command.value,
        )

    @device_command(strong=True)
    def get_value(self, **kwargs):
        """
        Send command with getting value from device
        :return: answered value from device
        """
        # raise NotImplementedError
        # command = None
        # value = None
        return self.device.read(**kwargs)

    @device_command(strong=True)
    def read(self, **kwargs):
        """
        Send command with getting value from device
        :return: answered value from device
        """
        return self.device.read(**kwargs)

    def get_last_answer(self):
        return self._last_answer

    def _handle_exception(self, e):
        s = traceback.format_exc()
        # print(s)
        raise e


class AbstractControllerManyDevices(AbstractController):

    devices = None

    def setup(self):
        for device in self.devices:
            device.setup()

    def destructor(self):
        if self._thread is not None:
            self._thread.join()
        for device in self.devices:
            device.destructor()

    @AbstractController.device_command(strong=True)
    def read(self, device_num=0, **kwargs):
        """
        Send command with getting value from device
        :return: answered value from device
        """
        return self.devices[device_num].read(**kwargs)

    @AbstractController.device_command(strong=True)
    def get_value(self, device_num=0, **kwargs):
        return self.devices[device_num].read(**kwargs)

    @AbstractController.device_command()
    def _exec_command(self, command: BaseCommand):
        return self.devices[command.device_num].exec_command(**command.kwargs)

    @AbstractController.device_command()
    def exec_command(self, device_num=0, **kwargs):
        """
        Send command with value to sensor
        :return: answered value from sensor
        """
        return self.devices[device_num].exec_command(**kwargs)
