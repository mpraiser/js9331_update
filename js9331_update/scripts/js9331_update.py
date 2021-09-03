import click
import multiprocessing
import time
from typing import Optional
from js9331_update.tftp_server import start_tftp_server
from js9331_update.updater import Updater


@click.command()
@click.option(
    "--com", "-c",
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
    help="IP of TFTP server (this PC).",
    required=True
)
@click.option(
    "--server_port", "-spt",
    type=int,
    help="Port of TFTP server (this PC).",
    default=69,
    show_default=True
)
@click.option(
    "--board_ip", "-bip",
    type=str,
    help="IP of JS9331 board. (DO NOT use x.x.x.1)",
    required=True
)
@click.option(
    "--path", "-p",
    type=str,
    help="Path of firmware.",
    required=True
)
@click.argument(
    "firmware",
    type=str,
    required=True
)
def js9331_update(
        com: Optional[str], baud_rate: int,
        server_ip: str, server_port: int, board_ip: str,
        path: str, firmware: str
):

    multiprocessing.Process(
        target=start_tftp_server,
        args=(
            path,
            server_ip,
            server_port
            ),
        daemon=True).start()

    js9331 = Updater(com, baud_rate, print_=click.echo)
    js9331.ensure_uboot()
    time.sleep(3)
    js9331.execute(f"setenv serverip {server_ip}\n")
    js9331.execute(f"setenv ipaddr {board_ip}\n")
    js9331.execute(f"tftp 0x80002000 {firmware}\n")
    js9331.execute(f"erase 0x9f020000 +$filesize\n")
    js9331.execute(f"cp.b 0x80002000 0x9f020000 $filesize\n")
    js9331.send(f"reset\n")


if __name__ == "__main__":
    js9331_update()
