#!/bin/env python3

from config import load_config
from database_connector import DatabaseConnector
from logger import Logger
from networking import UnixSocketServer


def main():
    # Load configuration
    config = load_config("./config/config.yaml")

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
