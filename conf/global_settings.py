from ..utils import get_serial_port


LOCAL_MODE = True

SERIAL_PORT = get_serial_port()

ACCURATE_VAKUMETR_PORT = 1
CURRENT_SOURCE_PORT = 3

VALVES_CONFIGURATION = [
    {'PORT': 2, "NAME": "O_2", "IS_GAS": True},
    {'PORT': 3, "NAME": "N_2", "IS_GAS": True},
    {'PORT': 4, "NAME": "Ar", "IS_GAS": True},
    {'PORT': 17, "NAME": "C_2", "IS_GAS": True},
    {'PORT': 6, "NAME": "F_2", "IS_GAS": True},
    # {'PORT': 7, "NAME": "O_2", "IS_GAS": True},
    # {'PORT': 8, "NAME": "N_2", "IS_GAS": True},
    # {'PORT': 9, "NAME": "Ar", "IS_GAS": True},
    # {'PORT': 10, "NAME": "C_2", "IS_GAS": True},
    # {'PORT': 11, "NAME": "F_2", "IS_GAS": True},
    # {'PORT': 12, "NAME": "PUMP", "IS_GAS": False},
    # {'PORT': 13, "NAME": "AIR", "IS_GAS": False},
]

VALVE_LIST = list(map(lambda x: x.get('NAME'), VALVES_CONFIGURATION))
GAS_LIST = list(map(lambda x: x.get('NAME'), filter(lambda x: x.get("IS_GAS", False), VALVES_CONFIGURATION)))


TABLE_COLUMN_NAMES = ["Процесс", "Аргумент 1", "Аргумент 2", "Аргумент 3", "Комментарий"]

# Used in modbus communication method
DEFAULT_MODBUS_BAUDRATE = 19200
DEFAULT_MODBUS_TIMEOUT = 0.2
DEFAULT_MODBUS_INSTRUMENT_NUMBER = 1

DEFAULT_MODBUS_TERMODAT_BAUDRATE = 9600

# RRG_MODBUS = {
#     'DEVICE_PORT': '/dev/ttyUSB1',
#     'REGISTERS': {
#         'STATE_FLAGS_1': 2,
#         'SET_GAS_FLOW': 4,
#         'GET_GAS_FLOW': 5,
#     },
# }
RRG_MODBUS_DEVICE_PORT = '/dev/ttyUSB1'
