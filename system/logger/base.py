import string
import time
import random
import datetime
import os

import numpy as np


class BaseLogger(object):
    """
    Base class for system logger

    history_logs - potential numpy array for long time logs
    actual_logs - up-to-date data for the last time
    """
    duration = 5 * 60
    parameter_time_name = "Время"
    time_index = 0  # const

    session_name = None
    session_log_file_order = 1
    log_file_name = None
    logs_dir = "logs/"
    log_file_size_border = 1024 * 1024 * 200

    actual_logs_amount = 10000  # 10000
    actual_logs_buffer = 1000  # 1000
    step_to_history = 100  # 100

    history_logs = None
    actual_logs = None
    log_type = np.float32

    def __init__(self, parameter_names=None, duration=None):
        self.start_time = time.time()
        if parameter_names is None:
            parameter_names = []

        assert self.parameter_time_name not in parameter_names, \
            'Time can\'t be inside parameter names array'
        assert self.time_index == 0, f'Time parameter index must be 0, now - {self.time_index}'
        self.parameter_names = [self.parameter_time_name] + parameter_names
        self.parameters_amount = len(self.parameter_names)
        # print('Logs parameters:', self.parameters_amount, self.parameter_names)

        self.param_to_index = {name: i for i, name in enumerate(self.parameter_names)}

        self.duration = duration or self.duration

        self.actual_logs = np.zeros(
            (self.parameters_amount,
             self.actual_logs_amount + self.actual_logs_buffer)).astype(self.log_type)
        self._actual_index = 0

        self.session_name = self._generate_initial_session_name()
        self._prepare_new_log_file()

        if not os.path.exists(self.logs_dir):
            os.makedirs(self.logs_dir)

    def _prepare_new_log_file(self):
        self.log_file_name = self._get_new_log_file_name()
        with open(self.log_file_path, 'w') as log_file:
            log_file.write(','.join(map(lambda x: f'{x}', self.parameter_names)) + '\n')
            print('Header log file writing done!')

    def _get_new_log_file_name(self):
        now_time = str(datetime.datetime.now().replace(microsecond=0)).replace(' ', '-')

        order = self.session_log_file_order
        self.session_log_file_order += 1

        return f"{self.session_name}_n{order}_{now_time}.csv"

    def _generate_initial_session_name(self):
        letters = string.ascii_lowercase
        code = ''.join(random.choice(letters) for i in range(4))
        return f"{datetime.datetime.now().date()}_{code}"

    def current_time(self):
        return time.time() - self.start_time

    def add_logs(self, **kwargs):
        current_time = self.current_time()
        np_logs = np.zeros((self.parameters_amount,)).astype(self.log_type)
        np_logs[0] = current_time
        for name, value in kwargs.items():
            np_logs[self.param_to_index[name]] = value

        self._to_log_file(np_logs)
        self.actual_logs[:, self._actual_index] = np_logs
        if self._actual_index == self.actual_logs_amount + self.actual_logs_buffer - 1:
            to_history_array = self.actual_logs[:, :self.actual_logs_buffer:self.step_to_history]
            if self.history_logs is not None:
                self.history_logs = np.hstack((self.history_logs, to_history_array))
            else:
                self.history_logs = to_history_array

            # self.actual_logs = np.hstack((
            #     self.actual_logs[:, self.actual_logs_buffer:],
            #     np.zeros((self.parameters_amount, self.actual_logs_buffer)).astype(self.log_type)
            # ))
            self.actual_logs[:, :self.actual_logs_amount] = self.actual_logs[:, self.actual_logs_buffer:]
            self._actual_index = self.actual_logs_amount
        else:
            self._actual_index += 1

        # history_logs_shape = self.history_logs.shape if self.history_logs is not None else 0
        # print('Current logs:', self.actual_logs.shape, self._actual_index, history_logs_shape, )
        self.clear_old_history_logs()

    def clear_old_history_logs(self):
        border_time = self.current_time() - self.duration

        if (self.history_logs is None) or float(self.history_logs[0][0]) > border_time:
            return
        indexes = np.where(self.history_logs[0] > border_time)
        if type(indexes) == tuple:
            indexes = indexes[0]
        # print("next indexes:", indexes)
        if indexes.size == 0:
            self.history_logs = None
        else:
            self.history_logs = self.history_logs[:, indexes]

    @property
    def log_file_path(self):
        return os.path.join(self.logs_dir, self.log_file_name)

    def _to_log_file(self, np_array):
        try:
            file_size = os.path.getsize(self.log_file_path)
        except:
            file_size = 0
        print('Current file size:', file_size)
        if file_size > self.log_file_size_border:
            self._prepare_new_log_file()

        with open(self.log_file_path, 'a') as csv_file:
            csv_file.write(','.join(map(str, np_array)) + '\n')
            # df.to_csv(csv_file, header=False)

    def get_array_log(self, name):
        index = self.param_to_index[name]
        actual_param_logs = self.actual_logs[index][:self._actual_index]
        if self.history_logs is not None:
            return np.hstack((self.history_logs[index], actual_param_logs))
        return actual_param_logs
