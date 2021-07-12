"""
Based on Serial and U-boot, send command to update OpenWrt firmware.
"""

import serial
import time
from collections import deque


# COM configuration
PORT = "COM25"
BAUD_RATE = 115200
TIMEOUT = 0.1  # seconds
SERVER_IP = "192.168.1.110"
IPADDR = "192.168.1.251"
BIN = "lede-ar71xx-generic-tl-wr720n-v3-squashfs-factory.bin"


commands = deque([
    f"setenv serverip {SERVER_IP}\n",
    f"setenv ipaddr {IPADDR}\n",
    f"tftp 0x80002000 {BIN}\n",
    f"erase 0x9f020000 +$filesize\n",
    f"cp.b 0x80002000 0x9f020000 $filesize\n",
    f"reset\n"
])

com = serial.Serial(PORT, BAUD_RATE, timeout=TIMEOUT)
com.write("reboot\n".encode("utf-8"))

while True:
    raw_data: bytes = com.readline()
    if not raw_data:
        continue
    data = raw_data.decode(errors="ignore")
    print(data, end="")
    if data.startswith("Hit any key to stop autoboot"):
        com.write("\n".encode("utf-8"))
        break

com.write("\n".encode("utf-8"))

while len(commands) > 0:
    raw_data: bytes = com.readline()
    if not raw_data:
        continue
    # print(raw_data)
    data = raw_data.decode()
    print(data, end="")

    if data == "ar7240> ":
        command = commands.popleft()
        # print(f"[command] {command}")
        com.write(command.encode("utf-8"))

com.close()