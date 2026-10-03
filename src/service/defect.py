"""欠陥情報サービスモジュール。

欠陥情報に対するCRUD操作のビジネスロジックおよびトランザクション制御を提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from dao import DefectDAO
from model import Defect


class DefectService:
    """欠陥情報に関するビジネスロジックを処理するサービスクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _defect_dao (DefectDAO): 欠陥情報DAOインスタンス。
    """

    def __init__(self, logger: Logger) -> None:
        """DefectServiceのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger
        self._defect_dao = DefectDAO(self._logger)

    def create(self, conn: Connection, defect_data: Defect) -> bool:
        """欠陥レコードを作成する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            defect_data (Defect): 作成する欠陥データ。

        Returns:
            bool: 作成に成功した場合はTrue。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret = self._defect_dao.create(conn, defect_data)
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

    def read(self, conn: Connection, defect_data: Defect) -> list[Defect] | None:
        """欠陥レコードを検索・取得する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            defect_data (Defect): 検索条件を含む欠陥データ。

        Returns:
            list[Defect] | None: 取得された欠陥リスト。

        Raises:
            ValueError: 検索条件が不正な場合。
            RuntimeError: データベースエラーが発生した場合。
        """
        try:
            result: list[Defect] = self._defect_dao.read(conn, defect_data)
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, defect_data: Defect) -> bool:
        """欠陥レコードを更新する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            defect_data (Defect): 検索条件および更新値を含む欠陥データ。

        Returns:
            bool: 更新に成功した場合はTrue、更新対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._defect_dao.update(conn, defect_data)
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

    def delete(self, conn: Connection, defect_data: Defect) -> bool:
        """欠陥レコードを削除する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            defect_data (Defect): 検索条件を含む欠陥データ。

        Returns:
            bool: 削除に成功した場合はTrue、削除対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._defect_dao.delete(conn, defect_data)
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
