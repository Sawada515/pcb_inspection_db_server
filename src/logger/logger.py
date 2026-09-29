import logging
import socket
import sys
from logging.handlers import SysLogHandler


class Logger:
    def __init__(self, syslog_server_addr, service_name):
        self._syslog_server_addr = syslog_server_addr
        self._service_name = service_name

    def open_log(self):
        try:
            logger = logging.getLogger(self._service_name)
            logger.setLevel(logging.INFO)

            if logger.handlers:
                return logger

            formatter = logging.Formatter(
                f"{self._service_name}: %(levelname)s: %(message)s\n"
            )

            handler = SysLogHandler(
                address=(self._syslog_server_addr, 514),
                socktype=socket.SOCK_STREAM
            )

            handler.setFormatter(formatter)

            logger.addHandler(handler)

            return logger

        except ConnectionRefusedError as e:
            print(
                f"Connection refused to syslog server at {self._syslog_server_addr}: {e}",
                file=sys.stderr
            )

            sys.exit(-1)

        except (TimeoutError, socket.gaierror) as e:
            print(
                f"Timeout or address resolution error when connecting to syslog server at {self._syslog_server_addr}: {e}",
                file=sys.stderr
            )

            sys.exit(-1)

        except OSError as e:
            print(
                f"OS error when connecting to syslog server at {self._syslog_server_addr}: {e}",
                file=sys.stderr
            )

            sys.exit(-1)
