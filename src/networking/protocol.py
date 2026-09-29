import json
import socket
import struct
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RequestDataPayload:
    query_type: str
    resource_type: str
    data: Any


@dataclass
class RequestDataFormat:
    request_id: int
    payload: RequestDataPayload


@dataclass
class ResponseDataError:
    error_code: int
    message: str


@dataclass
class ResponseDataFormat:
    request_id: int
    status: str
    payload: Any | None
    error: ResponseDataError | None

    def to_dict(self) -> dict:
        return asdict(self)


class Protocol:
    def __init__(self):
        self._MAX_RECV_DATA_SIZE = 1024 * 5
        self._HEADER_SIZE = 4

    def recv_data_exact(self, sock: socket.socket, size: int) -> bytes:
        data: bytes = b""

        if size <= 0 or size > self._MAX_RECV_DATA_SIZE:
            raise ValueError(f"Invalid size: {size}")

        while len(data) < size:
            chunk = sock.recv(size - len(data))

            if not chunk:
                raise ConnectionError("Connection Disconnected")

            data += chunk

        return data

    def recv_data(self, sock: socket.socket) -> RequestDataFormat:
        try:
            # 4バイトのヘッダーを受信
            header = self.recv_data_exact(sock, self._HEADER_SIZE)
        except ConnectionError:
            raise ConnectionError("Connection Disconnected")
        except ValueError as e:
            raise ValueError(f"Invalid header size: {e}")

        # 4バイトを整数に戻す
        body_size = struct.unpack("!I", header)[0]

        # ヘッダーで指定されたサイズだけ受信
        try:
            body = self.recv_data_exact(sock, body_size)
        except ConnectionError:
            raise ConnectionError("Connection Disconnected")
        except ValueError as e:
            raise ValueError(f"Invalid body size: {e}")

        # JSON → dict
        try:
            data = json.loads(body.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}")

        print(data)

        return RequestDataFormat(
            request_id=data["request_id"],
            payload=RequestDataPayload(
                query_type=data["payload"]["query_type"],
                resource_type=data["payload"]["resource"],
                data=data["payload"]["data"]
            )
        )

    def send_data(self, sock: socket.socket, data: ResponseDataFormat, number_of_data_record: int) -> None:
        print(f"send_data: {data}")
        converted_data = data.to_dict()
        print(f"converted_data: {converted_data}")

        body = json.dumps(converted_data).encode("utf-8")

        header = struct.pack("!II", len(body), number_of_data_record)

        sock.sendall(header + body)
