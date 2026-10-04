#!/usr/bin/env python3

import json
import socket
import struct
import time
from dataclasses import asdict, dataclass
from typing import Any

from networking import protocol


@dataclass
class SendDataPayload:
    """リクエストのペイロード情報を保持するデータクラス。

    Attributes:
        query_type (str): クエリ種別 (create, read, update, delete)。
        resource_type (str): 対象リソース種別 (user_service, inspection_service等)。
        data (Any): リソース固有のリクエストデータ辞書。
    """

    query_type: str
    resource: str
    data: Any

@dataclass
class SendDataFormat:
    """クライアントから送信されるリクエストの全体フォーマット。

    Attributes:
        request_id (int): リクエスト識別子。
        payload (SendDataPayload): リクエストペイロード。
    """

    request_id: int
    payload: SendDataPayload

    def to_dict(self) -> dict:
        """オブジェクトを辞書形式に変換する。

        Returns:
            dict: 属性値を辞書化したもの。
        """
        return asdict(self)

SOCKET_PATH = "/tmp/database_server.sock"

def main():
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.connect(SOCKET_PATH)

    if client is None:
        print("Failed to create socket")
        return
    
    protocol_instance = protocol.Protocol()

    USER = "user_service"
    INSPECTION = "inspection_service"
    REQUEST = "request_service"
    STORE = "store_service"
    DEFECT = "defect_service"
    DEFECTTYPE = "defect_type_service"
    IMAGE = "image_service"

    #data={"user_id": "202521309", "role": "general", "uuid": "e0e970d5-3ef5-46f0-b1b4-ca946dae5e35", "user_status": "active"}

    """
        user_service:
            crate: ok, read: ok, update: ok, delete: ok
        store_service:
            create: unused, read: ok, update: ok, delete: unused
        defect_service:
            create: ok, read: ok, update: ok, delete: ok
        inspection_service:
            create: ok, read: ng, update: ok, delete: ok
        inspection_request_service:
            create: ok, read: ok, update: ok, delete: ok
        defect_type_service:
            maybe unused
        image_service:
            create: ok, read: ok, update: ok, delete: ok 
    """
    
    send_data = SendDataFormat(
        request_id=1,
        payload=SendDataPayload(
            query_type="delete",
            resource=IMAGE,
            data={"defect_id": 13}
        )
    )

    print(f"send_data: {send_data}")
    converted_data = send_data.to_dict()
    print(f"converted_data: {converted_data}")
   
    body = json.dumps(converted_data).encode("utf-8")
   
    header = struct.pack("!I", len(body))
    
    print(f"header: {header}")
    print(f"body: {body}")
    client.sendall(header + body)

    time.sleep(1)

    print("########################")
    print("Receiving data...")
    print("########################")

    recv_data_header = protocol_instance.recv_data_exact(client, 8)
    print(f"recv_data_header: {recv_data_header}")

    recv_data_body_size = struct.unpack("!I", recv_data_header[:4])[0]

    recv_data_body = protocol_instance.recv_data_exact(client, recv_data_body_size)
    print(f"recv_data_body: {recv_data_body}")

    client.close()

if __name__ == "__main__":
    main()
     