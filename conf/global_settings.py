# from ..utils import get_serial_port


LOCAL_MODE = True

# SERIAL_PORT = get_serial_port()
#
# ACCURATE_VAKUMETR_PORT = 1
# CURRENT_SOURCE_PORT = 3

VALVES_CONFIGURATION = []

VALVE_LIST = list(map(lambda x: x.get('NAME'), VALVES_CONFIGURATION))
GAS_LIST = list(map(lambda x: x.get('NAME'), filter(lambda x: x.get("IS_GAS", False), VALVES_CONFIGURATION)))


TABLE_COLUMN_NAMES = ["Процесс", "Аргумент 1", "Аргумент 2", "Аргумент 3", "Комментарий"]

# Used in modbus communication method
DEFAULT_MODBUS_BAUDRATE = 19200
DEFAULT_MODBUS_TIMEOUT = 0.2
DEFAULT_MODBUS_INSTRUMENT_NUMBER = 1

DEFAULT_MODBUS_TERMODAT_BAUDRATE = 9600

SAVE_ERROR_NOTIFICATIONS = True
