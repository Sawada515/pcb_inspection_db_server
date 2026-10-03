#!/usr/bin/env python3

import json
import socket
import struct
import time

from networking import protocol
from dataclasses import asdict, dataclass
from typing import Any

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

    #data={"user_id": "202521309", "role": "general", "uuid": "e0e970d5-3ef5-46f0-b1b4-ca946dae5e35", "user_status": "active"}

    """
        user_service:
            crate: ok, read: ok, update: ok, delete: ok
        store_service:
            create: unuse, read: ok, update: ok, delete: unuse
        defect_service:
            create: ng, read: ng, update: ng, delete: ng
        
    """
    
    
    send_data = SendDataFormat(
        request_id=1,
        payload=SendDataPayload(
            query_type="create",
            resource="defect_service",
            data={"defect_id": 1, "board_side": "top", "point": "20, 30, 50, 60", "area": 100, "defect_type_id": 1, "inspection_id": 1}
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
     