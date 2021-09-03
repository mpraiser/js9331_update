import click
import threading
from typing import Optional
from js9331_update.tftp_server import start_tftp_server
from js9331_update.updater import Updater


@click.command()
@click.option(
    "--port", "-p",
    type=str,
    help="COM port of the JS9331 board.",
    required=True
)
@click.option(
    "--baud_rate", "-b",
    type=int,
    help="Baud rate of COM.",
    default=115200,
    show_default=True
)
@click.option(
    "--server_ip", "-sip",
    type=str,
    required=True
)
@click.option(
    "--server_port",
    type=int,
    default=69,
    show_default=True
)
@click.option(
    "--board_ip", "-bip",
    type=str,
    required=True
)
@click.option(
    "--path", "-p",
    type=str,
    required=True
)
@click.argument(
    "firmware",
    type=str,
    required=True
)
def js9331_update(
        port: Optional[str], baud_rate: int,
        server_ip: str, server_port: int, board_ip: str,
        path: str, firmware: str
):
    threading.Thread(
        target=start_tftp_server,
        args=(
            path,
            server_ip,
            server_port
            ),
        daemon=True).start()

    js9331 = Updater(port, baud_rate)
    js9331.ensure_uboot()

    js9331.execute(f"setenv serverip {server_ip}\n")
    js9331.execute(f"setenv ipaddr {board_ip}\n")
    js9331.execute(f"tftp 0x80002000 {firmware}\n")
    js9331.execute(f"erase 0x9f020000 +$filesize\n")
    js9331.execute(f"cp.b 0x80002000 0x9f020000 $filesize\n")
    js9331.send(f"reset\n")


if __name__ == "__main__":
    js9331_update()
