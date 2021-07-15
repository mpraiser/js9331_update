import json

# the latest code of tftpy on Github fixes "bad file path" problem on windows
# but the latest version 0.8.1 on pip doesn't.
# so i'm directly using this package without pip temporarily
import tftpy


def start_tftp_server(path: str, ip: str, port: int):
    server = tftpy.TftpServer(path)
    server.listen(ip, port)


if __name__ == "__main__":
    with open("properties.json", "r") as fp:
        properties = json.load(fp)

    start_tftp_server(
        properties['path'],
        properties['server_ip'],
        properties['tftp_port']
    )
