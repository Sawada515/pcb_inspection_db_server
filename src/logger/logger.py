"""Syslogログ出力モジュール。

Syslogサーバー（TCP 514ポート）に対してフォーマット済みログを転送する
ロガーを生成します。
"""

import logging
import socket
import sys
from logging.handlers import SysLogHandler
from typing import ClassVar


class Logger:
    """Syslogハンドラーを設定したロガーを初期化・提供するクラス。

    Attributes:
        _syslog_server_addr (str): SyslogサーバーのホストまたはIPアドレス。
        _service_name (str): サービス識別名。
    """


    def __init__(self, syslog_server_addr: str, service_name: str, facility: str) -> None:
        """Loggerのインスタンスを初期化する。

        Args:
            syslog_server_addr (str): Syslogサーバーのアドレス。
            service_name (str): サービス名。
            facility (str): ファシリティ。
        """
        self._syslog_server_addr = syslog_server_addr
        self._service_name = service_name
        self._facility = self._FACILITY_MAP.get(facility.lower(), SysLogHandler.LOG_USER)

    def open_log(self) -> logging.Logger:
        """Syslogハンドラーを登録したLoggerインスタンスを生成・取得する。

        Returns:
            logging.Logger: 設定済みのロガーオブジェクト。

        Raises:
            SystemExit: Syslogサーバーへの接続拒否、タイムアウト、アドレス解決失敗、
                OSエラーが発生した場合にプロセスを終了 (-1) します。
        """
        try:
            logger = logging.getLogger(self._service_name)
            logger.setLevel(logging.INFO)

            if logger.handlers:
                return logger

            formatter = logging.Formatter(
                "%(message)s"
            )

            handler = SysLogHandler(
                address=(self._syslog_server_addr, 514),
                facility=self._facility,
                socktype=socket.SOCK_STREAM
            )

            handler.ident = f"{self._service_name}: "

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

    _FACILITY_MAP: ClassVar[dict[str, int]] = {
        "kern": SysLogHandler.LOG_KERN,
        "user": SysLogHandler.LOG_USER,
        "mail": SysLogHandler.LOG_MAIL,
        "daemon": SysLogHandler.LOG_DAEMON,
        "auth": SysLogHandler.LOG_AUTH,
        "syslog": SysLogHandler.LOG_SYSLOG,
        "lpr": SysLogHandler.LOG_LPR,
        "news": SysLogHandler.LOG_NEWS,
        "uucp": SysLogHandler.LOG_UUCP,
        "cron": SysLogHandler.LOG_CRON,
        "authpriv": SysLogHandler.LOG_AUTHPRIV,
        "ftp": SysLogHandler.LOG_FTP,
        "local0": SysLogHandler.LOG_LOCAL0,
        "local1": SysLogHandler.LOG_LOCAL1,
        "local2": SysLogHandler.LOG_LOCAL2,
        "local3": SysLogHandler.LOG_LOCAL3,
        "local4": SysLogHandler.LOG_LOCAL4,
        "local5": SysLogHandler.LOG_LOCAL5,
        "local6": SysLogHandler.LOG_LOCAL6,
        "local7": SysLogHandler.LOG_LOCAL7
    }