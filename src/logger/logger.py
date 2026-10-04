"""Syslogログ出力モジュール。

Syslogサーバー（TCP 514ポート）に対してフォーマット済みログを転送する
ロガーを生成します。
"""

import logging
import socket
import sys
from logging.handlers import SysLogHandler


class Logger:
    """Syslogハンドラーを設定したロガーを初期化・提供するクラス。

    Attributes:
        _syslog_server_addr (str): SyslogサーバーのホストまたはIPアドレス。
        _service_name (str): サービス識別名。
    """

    def __init__(self, syslog_server_addr: str, service_name: str):
        """Loggerのインスタンスを初期化する。

        Args:
            syslog_server_addr (str): Syslogサーバーのアドレス。
            service_name (str): サービス名。
        """
        self._syslog_server_addr = syslog_server_addr
        self._service_name = service_name

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
                f"{self._service_name}: %(levelname)s: %(message)s"
            )

            handler = SysLogHandler(
                address=(self._syslog_server_addr, 514),
                socktype=socket.SOCK_STREAM
            )

            handler.ident = ""

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
