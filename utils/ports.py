
def get_serial_port():
    import subprocess
    try:
        a = subprocess.run("dmesg | grep tty | grep FTDI", shell=True, capture_output=True)
        line = a.stdout.decode("ASCII")
        # print("LINE", line)
        s = "ttyUSB"
        index = line.find(s) + len(s)
        serial_port = "/dev/" + s + line[index]
        # print("# SERIAL PORT:", serial_port)
        return serial_port  # /dev/ttyUSB0
    except:
        print("[ERR] SERIAL PORT ERROR! RETURN DEFAULT")
        return "/dev/ttyUSB0"


def get_available_usb_ports():
    import subprocess
    try:
        a = subprocess.run("ls /dev/ttyUSB*", shell=True, capture_output=True)
        line = a.stdout.decode("ASCII")
        print("PORTS", line)
        return line.strip().split()
    except Exception as e:
        print("ERROR [get_available_usb_ports]:", e)
        return []
