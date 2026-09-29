import os
import socket
import struct
import threading
import time
from pathlib import Path

from database_connector import DatabaseConnector
from networking import (
    Protocol,
    RequestDataFormat,
    ResponseDataError,
    ResponseDataFormat,
)
from request_router import RequestRouter


class UnixSocketServer:
    def __init__(self, socket_file_path: str, logger, db_connection: DatabaseConnector):
        if socket_file_path is None:
            raise ValueError("Socket path must be provided")
        if logger is None:
            raise ValueError("Logger must be provided")

        self._logger = logger

        self._socket_file_path = Path(socket_file_path)
        if self._socket_file_path.exists():
            self._socket_file_path.unlink()

        self._server_socket = socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM
        )

        self._request_router = RequestRouter(self._logger)
        self._protocol = Protocol()

        self._db_connection = db_connection

    def start(self):
        if self._socket_file_path.exists():
            self._socket_file_path.unlink()

        self._server_socket.bind(str(self._socket_file_path))
        self._server_socket.listen()

        try:
            while True:
                conn, _ = self._server_socket.accept()

                threading.Thread(
                    target=self.handle_client,
                    args=(conn,),
                    daemon=True
                ).start()
        finally:
            if self._socket_file_path.exists():
                self._socket_file_path.unlink()

    def handle_client(self, conn: socket.socket):
        db_conn = None
        db_commit_flag = False

        # 1. データベース接続の取得（DBダウン時はリトライ後にプロセス全体を終了）
        try:
            db_conn = self._db_connection.get_connection()
        except RuntimeError as e:
            self._logger.error(
                f"Error occurred while getting database connection: {e}")

            time.sleep(0.5)

            try:
                db_conn = self._db_connection.get_connection()
            except RuntimeError as retry_err:
                self._logger.critical(
                    f"Fatal database error on retry: {retry_err}. Terminating server process.")

                try:
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=-1,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Database connection error")
                        ),
                        0
                    )
                finally:
                    conn.close()

                # 子スレッドからサーバープロセス全体を直ちに終了
                os._exit(1)

        # 2. クライアント通信ループ
        try:
            while True:
                recv_request_data: RequestDataFormat = self._protocol.recv_data(
                    conn)

                if recv_request_data is None:
                    self._request_router._logger.error(
                        "Received request data is None")
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=-1,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Received request data is None")
                        ),
                        0
                    )
                    break

                if recv_request_data.request_id is None:
                    self._request_router._logger.error(
                        "Received request_id is None")
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=-1,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Received request_id is None")
                        ),
                        0
                    )
                    break
                else:
                    request_id = recv_request_data.request_id

                if recv_request_data.payload is None:
                    self._request_router._logger.error(
                        f"Received payload is None for request_id: {request_id}")
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=request_id,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Received payload is None")
                        ),
                        0
                    )
                    break
                else:
                    payload = recv_request_data.payload

                if payload.resource_type is None:
                    self._request_router._logger.error(
                        f"Received resource_type is None for request_id: {request_id}")
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=request_id,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Received resource_type is None")
                        ),
                        0
                    )
                    break
                else:
                    resource_type = payload.resource_type

                if payload.query_type is None:
                    self._request_router._logger.error(
                        f"Received query_type is None for request_id: {request_id}")
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=request_id,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Received query_type is None")
                        ),
                        0
                    )
                    break
                else:
                    query_type = payload.query_type

                if payload.data is None:
                    self._request_router._logger.error(
                        f"Received data is None for request_id: {request_id}")
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=request_id,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Received data is None")
                        ),
                        0
                    )
                    break
                else:
                    request_data = payload.data

                print(request_id, resource_type, query_type, request_data)

                if query_type != "read":
                    db_commit_flag = True
                else:
                    db_conn.commit()

                # クエリ実行（DBエラー時は他スレッドも道連れに落とす）
                try:
                    result = self._request_router.dispatch(
                        request_resource_str=resource_type,
                        query_type_str=query_type,
                        request_data=request_data,
                        conn=db_conn
                    )
                except RuntimeError as db_err:
                    self._logger.critical(
                        f"Database query error in router: {db_err}. Terminating server process.")
                    os._exit(1)

                # レスポンス返却
                if result is None:
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=request_id,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Request processing returned None")
                        ),
                        0
                    )
                elif result is False:
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=request_id,
                            status="error",
                            payload=None,
                            error=ResponseDataError(
                                error_code=-1, message="Request processing failed")
                        ),
                        0
                    )
                elif result is True:
                    self._protocol.send_data(
                        conn,
                        ResponseDataFormat(
                            request_id=request_id,
                            status="success",
                            payload=None,
                            error=None
                        ),
                        0
                    )
                else:
                    if isinstance(result, list):
                        send_data = [r.to_dict() for r in result]
                        self._protocol.send_data(
                            conn,
                            ResponseDataFormat(
                                request_id=request_id,
                                status="success",
                                payload=send_data,
                                error=None
                            ),
                            len(result)
                        )
                    else:
                        self._protocol.send_data(
                            conn,
                            ResponseDataFormat(
                                request_id=request_id,
                                status="success",
                                payload=result.to_dict(),
                                error=None
                            ),
                            1                   # <= 固定長
                        )

                if db_commit_flag:
                    db_conn.commit()



        except BrokenPipeError as e:
            pid = self._get_pid(conn)
            self._logger.error(f"Destination PID: {pid}, BrokenPipeError: {e}")

        except RuntimeError as e:
            pid = self._get_pid(conn)
            self._logger.error(
                f"Destination PID: {pid}, Unexpected client handler error: {e}")

        finally:
            # コネクションはコミット成否に関わらず確実にプールへ返却
            if db_conn is not None:
                if db_commit_flag:
                    try:
                        db_conn.commit()
                    except RuntimeError as commit_err:
                        self._logger.critical(
                            f"Database commit failed: {commit_err}. Terminating server process.")
                        os._exit(1)

                self._db_connection.release_connection(db_conn)

            conn.close()

    def _get_pid(self, conn: socket.socket) -> int:
        SO_PEERCRED = getattr(socket, "SO_PEERCRED", 17)
        return struct.unpack(
            "3i",
            conn.getsockopt(
                socket.SOL_SOCKET,
                SO_PEERCRED,
                struct.calcsize("3i")
            )
        )[0]
