#!/bin/env python3
"""PCB検査データベースサーバー メインエントリーポイント。

設定ファイルの読み込み、ロガーの初期化、データベース接続プールの初期化、
およびUNIXドメインソケットサーバーの起動を行います。
"""

from pathlib import Path

from src.config import load_config
from src.database_connector import DatabaseConnector
from src.logger import Logger
from src.networking import UnixSocketServer

CONFIG_FILE_PATH = Path(__file__).resolve().parent / "config" / "config.yaml"

def main() -> None:
    """サーバーアプリケーションを初期化し、リクエスト受付を開始する。

    設定ファイルを読み込み、ロガーおよびDB接続プールを構成した上で、
    UNIXドメインソケットサーバーを起動してクライアントからの要求を処理します。
    """
    # Load configuration
    config = load_config(str(CONFIG_FILE_PATH))

    # Initialize logger
    logger = Logger(config.syslog_server.syslog_server_ip,
                    config.syslog_server.service_name)
    logger_client = logger.open_log()

    # Initialize database connector
    db_connector = DatabaseConnector(
        host=config.database.host,
        port=config.database.port,
        user=config.database.username,
        password=config.database.password,
        database=config.database.database_name
    )

    # Initialize Unix socket server
    socket_server = UnixSocketServer(
        socket_file_path=config.socket.uds_socket_path,
        logger=logger_client,
        db_connection=db_connector
    )

    # Start the server
    socket_server.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
