import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Database:
    host: str
    port: int
    username: str
    password: str
    database_name: str


@dataclass
class syslog_server:
    syslog_server_ip: str
    service_name: str


@dataclass
class uds_socket:
    uds_socket_path: str


@dataclass
class Config:
    database: Database
    syslog_server: syslog_server
    socket: uds_socket


def load_config(config_file_path: str) -> Config:
    path = Path(config_file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Configuration file not found: {config_file_path}")

    try:
        with open(config_file_path, 'r') as file:
            config_data = yaml.safe_load(file)

            if config_data is None:
                print(
                    f"Configuration file is empty: {config_file_path}", file=sys.stderr)

                raise RuntimeError(
                    f"Configuration file is empty: {config_file_path}")

            if not isinstance(config_data, dict):
                raise yaml.YAMLError(
                    f"Configuration file is not a valid YAML dictionary: {config_file_path}")

    except yaml.YAMLError:
        raise ValueError(
            f"Error parsing YAML configuration file: {config_file_path}.")

    except OSError:
        raise OSError(f"Error reading configuration file: {config_file_path}.")

    try:
        raw_database_config = config_data.get("database")
        if raw_database_config is None:
            raise KeyError("Missing 'database' configuration section.")

        database_config = Database(
            host=raw_database_config["host"],
            port=raw_database_config["port"],
            username=raw_database_config["user"],
            password=raw_database_config["password"],
            database_name=raw_database_config["database_name"]
        )

        raw_syslog_server_config = config_data.get("syslog_server")
        if raw_syslog_server_config is None:
            raise KeyError("Missing 'syslog_server' configuration section.")

        syslog_server_config = syslog_server(
            syslog_server_ip=raw_syslog_server_config["ip_addr"],
            service_name=raw_syslog_server_config["service_name"]
        )

        raw_socket_config = config_data.get("socket")
        if raw_socket_config is None:
            raise KeyError("Missing 'socket' configuration section.")

        socket_config = uds_socket(
            uds_socket_path=raw_socket_config["socket_path"]
        )

    except KeyError as e:
        raise KeyError(f"Missing required configuration key: {e}")

    return Config(
        database=database_config,
        syslog_server=syslog_server_config,
        socket=socket_config
    )


if __name__ == "__main__":
    config_file_path = "config.yaml"

    config = load_config(config_file_path)
    print("Configuration loaded successfully.")
    print(config)
