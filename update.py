"""
Based on Serial and U-boot, send command to update OpenWrt firmware.
"""

import time
import threading
import json

from js9331_update.tftp_server import start_tftp_server
from js9331_update.updater import Updater


with open("properties.json", "r") as fp:
    properties = json.load(fp)

# start TFTP server
threading.Thread(
    target=start_tftp_server,
    args=(
        properties['path'],
        properties['server_ip'],
        properties['tftp_port']
        ),
    daemon=True).start()

js9331 = Updater(properties["com"], properties["baud_rate"])
js9331.ensure_uboot()
time.sleep(3)  # let the board be fully started.
js9331.execute(f"setenv serverip {properties['server_ip']}\n")
js9331.execute(f"setenv ipaddr {properties['ipaddr']}\n")
js9331.execute(f"tftp 0x80002000 {properties['bin']}\n")
# while True:
#     success = js9331.execute(
#         f"tftp 0x80002000 {properties['bin']}\n",
#         time_limit=10
#     )
#     if success:
#         break
#     else:
#         js9331.send(CANCEL)
js9331.execute(f"erase 0x9f020000 +$filesize\n")
js9331.execute(f"cp.b 0x80002000 0x9f020000 $filesize\n")
js9331.send(f"reset\n")
