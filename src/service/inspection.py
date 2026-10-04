"""基板検査情報サービスモジュール。

検査結果情報に対するCRUD操作のビジネスロジックおよびトランザクション制御を提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from src.dao import InspectionDAO
from src.model import Inspection


class InspectionService:
    """基板検査情報に関するビジネスロジックを処理するサービスクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _inspection_dao (InspectionDAO): 検査情報DAOインスタンス。
    """

    def __init__(self, logger: Logger) -> None:
        """InspectionServiceのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger
        self._inspection_dao = InspectionDAO(self._logger)

    def create(self, conn: Connection, inspection_data: Inspection) -> bool:
        """検査レコードを作成する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            inspection_data (Inspection): 作成する検査データ。

        Returns:
            bool: 作成に成功した場合はTrue。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret = self._inspection_dao.create(conn, inspection_data)
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

    def read(
        self, conn: Connection, inspection_data: Inspection
    ) -> list[Inspection] | None:
        """検査レコードを検索・取得する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            inspection_data (Inspection): 検索条件を含む検査データ。

        Returns:
            list[Inspection] | None: 取得された検査リスト。

        Raises:
            ValueError: 検索条件が不正な場合。
            RuntimeError: データベースエラーが発生した場合。
        """
        try:
            result: list[Inspection] = self._inspection_dao.read(
                conn, inspection_data)
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, inspection_data: Inspection) -> bool:
        """検査レコードを更新する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            inspection_data (Inspection): 検索条件および更新値を含む検査データ。

        Returns:
            bool: 更新に成功した場合はTrue、更新対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._inspection_dao.update(conn, inspection_data)
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

    def delete(self, conn: Connection, inspection_data: Inspection) -> bool:
        """検査レコードを削除する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            inspection_data (Inspection): 検索条件を含む検査データ。

        Returns:
            bool: 削除に成功した場合はTrue、削除対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._inspection_dao.delete(conn, inspection_data)
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
