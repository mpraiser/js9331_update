import serial
import time
import click
from typing import Callable, Optional
from functools import partial


class Timeout(Exception):
    pass


CANCEL = "\003\n"
UBOOT_READY = "ar7240> "


class Updater:
    def __init__(
            self, port: str,
            baud_rate: int, *,
            timeout: float = 0.1,
            print_: Callable = print):
        self.com = serial.Serial(port, baud_rate, timeout=timeout)
        if print_ == print:
            self.print_ = partial(print, end="")
        elif print_ == click.echo:
            self.print_ = partial(click.echo, nl="")
        else:
            self.print_ = print_

    def cancel_and_activate(self):
        self.send(CANCEL)
        self.send("\n")

    def recv(self) -> str:
        while True:
            raw = self.com.readline()
            if not raw:
                continue
            data = raw.decode(errors="ignore")
            self.print_(data)
            return data

    def send(self, data: str):
        self.com.write(data.encode("utf-8"))

    def execute(self, command: str, time_limit: float = None) -> bool:
        """
        blocking execute command
        :param command: command string to send
        :param time_limit: if execution time exceeds this limit, execution will restart.
        """
        self.send(command)
        ret = self.ensure(
            (self.is_ready, self.exit),
            time_limit=time_limit
        )
        return ret

    def ensure_uboot(self):
        self.cancel_and_activate()
        time.sleep(0.5)
        self.send("reboot\n")
        self.ensure(
            (
                lambda d: d.startswith("Hit any key to stop autoboot"),
                partial(self.send, "\n")
            ),
            (
                self.is_ready,
                self.exit
            )
        )

    def ensure_ready(self):
        self.ensure(
            (self.is_ready, self.exit)
        )

    @staticmethod
    def exit():
        """placeholder used as break in ensure()"""
        pass

    def ensure(
            self,
            *targets: tuple[Callable[[str], bool], Callable],
            time_limit: Optional[float] = None
    ) -> bool:
        """
        Circularly receive data and do something on certain condition, with time limit.
        :param targets: (condition, callback).
            the most special callback is self.exit, used to exit iteration.
        :param time_limit:
        :return: whether is successfully ensured within time limit
        """
        t_start = time.time()
        while time_limit is None or time.time() - t_start < time_limit:
            data = self.recv()
            for condition, callback in targets:
                if condition(data):
                    if callback is self.exit:
                        return True
                    else:
                        callback()
        return False

    @staticmethod
    def is_ready(data: str) -> bool:
        return data == UBOOT_READY

    def close(self):
        self.com.close()
