from utils import get_serial_port


SERIAL_PORT = get_serial_port()

ACCURATE_VAKUMETR_PORT = 1
ACCURATE_VAKUMETR_USB_PORT = '/dev/ttyUSB0'  # FOR CVD-GRAPHENE USE USB1 (?)
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


CORGY = 1
