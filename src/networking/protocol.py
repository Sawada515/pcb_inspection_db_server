"""UNIXドメインソケット通信プロトコルモジュール。

クライアント・サーバー間のリクエスト・レスポンスフォーマット定義と、
ソケットを介したバイナリヘッダー付きJSONメッセージの送受信を提供します。
"""

import json
import socket
import struct
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RequestDataPayload:
    """リクエストのペイロード情報を保持するデータクラス。

    Attributes:
        query_type (str): クエリ種別 (create, read, update, delete)。
        resource_type (str): 対象リソース種別 (user_service, inspection_service等)。
        data (Any): リソース固有のリクエストデータ辞書。
    """

    query_type: str
    resource_type: str
    data: Any


@dataclass
class RequestDataFormat:
    """クライアントから送信されるリクエストの全体フォーマット。

    Attributes:
        request_id (int): リクエスト識別子。
        payload (RequestDataPayload): リクエストペイロード。
    """

    request_id: int
    payload: RequestDataPayload


@dataclass
class ResponseDataError:
    """エラーレスポンスの詳細情報を保持するデータクラス。

    Attributes:
        error_code (int): エラーコード。
        message (str): エラーメッセージ。
    """

    error_code: int
    message: str


@dataclass
class ResponseDataFormat:
    """サーバーからクライアントへ返却されるレスポンスの全体フォーマット。

    Attributes:
        request_id (int): 対応するリクエスト識別子。
        status (str): 処理ステータス ("success" または "error")。
        payload (Any | None): レスポンスデータ。
        error (ResponseDataError | None): エラー情報（エラー発生時のみ設定）。
    """

    request_id: int
    status: str
    payload: Any | None
    error: ResponseDataError | None

    def to_dict(self) -> dict:
        """オブジェクトを辞書形式に変換する。

        Returns:
            dict: 属性値を辞書化したもの。
        """
        return asdict(self)


class Protocol:
    """バイナリヘッダー付きJSON通信の送受信プロトコルを処理するクラス。

    受信プロトコル:
        [4バイト: ボディ長(Big-Endian uint32)] + [JSONボディ]

    送信プロトコル:
        [4バイト: ボディ長(Big-Endian uint32)] + [4バイト: レコード件数(Big-Endian uint32)] + [JSONボディ]

    Attributes:
        _MAX_RECV_DATA_SIZE (int): 1回に受信可能な最大ボディサイズ（バイト）。
        _HEADER_SIZE (int): 受信ヘッダーのバイトサイズ。
    """

    def __init__(self):
        """Protocolのインスタンスを初期化する。"""
        self._MAX_RECV_DATA_SIZE = 1024 * 5
        self._HEADER_SIZE = 4

    def recv_data_exact(self, sock: socket.socket, size: int) -> bytes:
        """指定したバイト数を正確にソケットから受信する。

        Args:
            sock (socket.socket): 通信ソケット。
            size (int): 受信するバイト数。

        Returns:
            bytes: 受信したバイト列。

        Raises:
            ValueError: サイズが不正（0以下または最大許容サイズ超過）の場合。
            ConnectionError: 受信途中で接続が切断された場合。
        """
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
        """ソケットからヘッダーおよびJSONボディを受信し、RequestDataFormatを構築する。

        Args:
            sock (socket.socket): 受信元のソケット。

        Returns:
            RequestDataFormat: 受信・構築されたリクエストオブジェクト。

        Raises:
            ConnectionError: ソケット接続が切断された場合。
            ValueError: ヘッダー/ボディサイズが不正、またはJSONデコードに失敗した場合。
        """
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
        """レスポンスオブジェクトをJSONエンコードし、バイナリヘッダーを付与して送信する。

        Args:
            sock (socket.socket): 送信先のソケット。
            data (ResponseDataFormat): 送信するレスポンスデータ。
            number_of_data_record (int): レスポンスに含まれるレコード件数。
        """
        print(f"send_data: {data}")
        converted_data = data.to_dict()
        print(f"converted_data: {converted_data}")

        body = json.dumps(converted_data).encode("utf-8")

        header = struct.pack("!II", len(body), number_of_data_record)

        sock.sendall(header + body)
