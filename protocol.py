import socket
import json


HEADERSIZE = 66
"""size=10,type=3[TXT,AUD,IMG,ERR,JSN],filename=50;"""


def _get_information(sock: socket.socket, size: int) -> bytes:
    recv_info_length = 0
    full_info = b""
    while recv_info_length < size:
        got_info = sock.recv(size-recv_info_length)
        if got_info == b"":
            raise ConnectionError("Received less than expected")
        else:
            recv_info_length += len(got_info)
            full_info += got_info
    return full_info


def recv_information(sock: socket.socket) -> list:
    header = _get_information(sock, HEADERSIZE).decode()
    splitted_header = header.split(",")
    size = splitted_header[0]
    type = splitted_header[1]
    filename = splitted_header[2].replace("0", "")
    filename = filename[:-1]
    data = _get_information(sock, int(size))
    if type == "TXT" or type == "JSN":
        return [type, data.decode()]
    elif type == "ERR":
        raise Exception(data.decode())
    elif type == "AUD" or type == "IMG":
        file = open(f"recv_files/{filename}", "wb")
        file.write(data)
        file.close()
        return [type, f"recv_files/{filename}"]
    raise Exception("Unknown Exception")


def send_text(sock: socket.socket, text: str, type = "TXT") -> None:
    size = str(len(text.encode()))
    size_of_size = len(size)
    amount_of_zero = 10 - size_of_size
    size = "0"*amount_of_zero + str(size)
    filename = "0"*50
    header = f"{size},{type},{filename};"
    sock.sendall(header.encode())
    sock.sendall(text.encode())


def send_error(sock: socket.socket, error_text: str) -> None:
    size = str(len(error_text.encode()))
    size_of_size = len(size)
    amount_of_zero = 10 - size_of_size
    size = "0" * amount_of_zero + str(size)
    type = "ERR"
    filename = "0"*50
    header = f"{size},{type},{filename};"
    sock.sendall(header.encode())
    sock.sendall(error_text.encode())


def send_file(sock: socket.socket, filename: str, type: str) -> None:
    file = open(f"{filename}", "rb")
    data = file.read()
    size = str(len(data))
    size_of_size = len(size)
    amount_of_zero = 10 - size_of_size
    size = "0" * amount_of_zero + str(size)
    file.close()
    filename_size = len(filename.encode())
    amount_of_zero = 50 - filename_size
    filename = "0" * amount_of_zero + filename
    header = f"{size},{type},{filename};"
    sock.sendall(header.encode())
    sock.sendall(data)

def send_jason(socket, jason_object):
    text = json.dumps(jason_object)
    send_text(socket, text, type="JSN")
