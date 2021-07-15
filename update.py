"""
Based on Serial and U-boot, send command to update OpenWrt firmware.
"""

import serial
import threading
import json
import time
from collections import deque
from tftp_server import start_tftp_server


with open("properties.json", "r") as fp:
    properties = json.load(fp)

# default_properties = {
#     # COM configurations
#     "com": "COM25",
#     "baud_rate": 115200,
#     "com_timeout": 0.1,  # seconds, default 0.1
#     # TFTP configurations
#     "server_ip": "192.168.1.110",
#     "ipaddr": "192.168.1.251",
#     "bin": "openwrt-ar71xx-generic-tl-wr710n-v1-squashfs-factory.bin",
#     "path": "firmware",
#     "tftp_port": 69
# }

# commands to send in u-boot stage
raw_commands = [
    f"setenv serverip {properties['server_ip']}\n",
    f"setenv ipaddr {properties['ipaddr']}\n",
    f"tftp 0x80002000 {properties['bin']}\n",
    f"erase 0x9f020000 +$filesize\n",
    f"cp.b 0x80002000 0x9f020000 $filesize\n",
    f"reset\n"
]
commands = deque(raw_commands)

# start TFTP server

threading.Thread(
    target=start_tftp_server,
    args=(
        properties['path'],
        properties['server_ip'],
        properties['tftp_port']
        ),
    daemon=True).start()

com = serial.Serial(properties['com'], properties['baud_rate'], timeout=properties['com_timeout'])

# reboot into u-boot stage
com.write("\n".encode("utf-8"))  # invoke the terminal
com.write("reboot\n".encode("utf-8"))

while True:
    raw_data: bytes = com.readline()
    if not raw_data:
        continue
    data = raw_data.decode(errors="ignore")
    print(data, end="")
    if data.startswith("Hit any key to stop autoboot"):
        com.write("\n".encode("utf-8"))  # stop autoboot
        break
    if data == "ar7240> ":  # if already in u-boot, break
        break

time.sleep(3)  # wait to let eth0 and eth1 loaded by u-boot
com.write("\n".encode("utf-8"))

# send commands
while len(commands) > 0:
    raw_data: bytes = com.readline()
    if not raw_data:
        continue
    data = raw_data.decode()
    print(data, end="")
    if data == "ar7240> ":
        command = commands.popleft()
        # print(f"[command] {command}")
        com.write(command.encode("utf-8"))

com.close()
