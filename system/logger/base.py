import time

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

    def current_time(self):
        # print('Now time:', time.time())
        return time.time() - self.start_time

    def add_logs(self, **kwargs):
        current_time = self.current_time()
        np_logs = np.zeros((self.parameters_amount,)).astype(self.log_type)
        np_logs[0] = current_time
        for name, value in kwargs.items():
            np_logs[self.param_to_index[name]] = value

        self._to_log_file(np_logs)
        # print('EREWR',
        #       self.actual_logs[:][self._actual_index],
        #       self.actual_logs[:, self._actual_index].shape,
        #       self.actual_logs[:].shape,
        #       self.actual_logs.shape,
        #       )
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

        history_logs_shape = self.history_logs.shape if self.history_logs is not None else 0
        # print('Current logs:', self.actual_logs.shape, self._actual_index, history_logs_shape, )
        self.clear_old_history_logs()

    def clear_old_history_logs(self):
        border_time = self.current_time() - self.duration
        # print('TIME:', border_time)
        # if self.history_logs is not None:
        #     print('TIME', border_time, float(self.history_logs[0][0]),
        #           float(self.history_logs[0][0]) > border_time)

        if (self.history_logs is None) or float(self.history_logs[0][0]) > border_time:
            return
        # print('\n\nCLEAR!!!!!!!!!!!!!!!!!!\n\n')
        # print('ZER[0]', self.history_logs[0])
        indexes = np.where(self.history_logs[0] > border_time)
        if type(indexes) == tuple:
            indexes = indexes[0]
        # print("next indexes:", indexes)

        self.history_logs = self.history_logs[:, indexes]

    def _to_log_file(self, np_array):
        pass

    def get_array_log(self, name):
        index = self.param_to_index[name]
        actual_param_logs = self.actual_logs[index][:self._actual_index]
        if self.history_logs is not None:
            return np.hstack((self.history_logs[index], actual_param_logs))
        return actual_param_logs
