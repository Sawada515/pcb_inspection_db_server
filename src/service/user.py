"""ユーザー情報サービスモジュール。

ユーザー情報に対するCRUD操作のビジネスロジックおよびトランザクション制御を提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from src.dao import UserDAO
from src.model import User


class UserService:
    """ユーザー情報に関するビジネスロジックを処理するサービスクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _user_dao (UserDAO): ユーザーDAOインスタンス。
    """

    def __init__(self, logger: Logger) -> None:
        """UserServiceのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger

        self._user_dao = UserDAO(self._logger)

    def create(self, conn: Connection, user_data: User) -> bool:
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
            ret = self._user_dao.create(conn, user_data)
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

    def read(self, conn: Connection, user_data: User) -> list[User] | None:
        """ユーザーレコードを検索・取得する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            user_data (User): 検索条件を含むユーザーデータ。

        Returns:
            list[User] | None: 取得されたユーザーリスト。

        Raises:
            ValueError: 検索条件が不正な場合。
            RuntimeError: データベースエラーが発生した場合。
        """
        try:
            result: list[User] = self._user_dao.read(conn, user_data)
        except ValueError:
            raise

        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, user_data: User) -> bool:
        """ユーザーレコードを更新する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            user_data (User): 検索条件および更新値を含むユーザーデータ。

        Returns:
            bool: 更新に成功した場合はTrue、更新対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._user_dao.update(conn, user_data)
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

    def delete(self, conn: Connection, user_data: User) -> bool:
        """ユーザーレコードを削除する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            user_data (User): 検索条件を含むユーザーデータ。

        Returns:
            bool: 削除に成功した場合はTrue、削除対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._user_dao.delete(conn, user_data)
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
