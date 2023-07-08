import subprocess

def get_serial_port():
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


def get_available_ttyusb_ports():
    try:
        a = subprocess.run("ls /dev/ttyUSB*", shell=True, capture_output=True)
        line = a.stdout.decode("ASCII")
        print("PORTS", line)
        return line.strip().split()
    except Exception as e:
        print("ERROR [get_available_ttyusb_ports]:", e)
        return []


def get_available_ttyusb_port_by_usb(usb_port: str) -> str:
    try:
        a = subprocess.run(f"sudo dmesg | grep ttyUSB | grep usb | grep {usb_port}",
                           shell=True, capture_output=True)
        line = a.stdout.decode("ASCII")
        words = list(filter(lambda x: "ttyUSB" in x, line.strip().split()))
        print('WORDS:', words)
        if len(words) > 0:
            return f"/dev/{words[0]}"
    except Exception as e:
        print(f"ERROR [get_available_ttyusb_port_by_usb {usb_port}]:", e)
    return ''
