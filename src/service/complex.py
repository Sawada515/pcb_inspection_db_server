"""
複雑なデータ操作を行うクラス。
"""


from logging import Logger

import mariadb
from mariadb import Connection

from src.dao import ComplexDAO
from src.model import *


class ComplexService:
    """複雑なデータ操作を行うビジネスロジックを処理するサービスクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _user_dao (UserDAO): ユーザーDAOインスタンス。
    """

    def __init__(self, logger: Logger) -> None:
        """ComplexServiceのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger

        self._user_dao = ComplexDAO(self._logger)

    def get_user_list(self, conn: Connection) -> list[UserList]:
        """ユーザーレコードを作成する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            user_data (User): 作成するユーザーデータ。

        Returns:
            bool: 作成に成功した場合はTrue。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret = self._user_dao.get_user_list(conn)
        except ValueError:
            raise
        except mariadb.Error as e:
            try:
                conn.rollback()
            except mariadb.Error:
                pass

            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return ret