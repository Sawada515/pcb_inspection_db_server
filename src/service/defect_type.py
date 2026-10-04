"""欠陥種別マスタサービスモジュール。

欠陥種別情報に対するCRUD操作のビジネスロジックおよびトランザクション制御を提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from src.dao import DefectTypeDAO
from src.model import DefectType


class DefectTypeService:
    """欠陥種別マスタに関するビジネスロジックを処理するサービスクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _defect_type_dao (DefectTypeDAO): 欠陥種別DAOインスタンス。
    """

    def __init__(self, logger: Logger) -> None:
        """DefectTypeServiceのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger
        self._defect_type_dao = DefectTypeDAO(self._logger)

    def create(self, conn: Connection, defect_type_data: DefectType) -> bool:
        """欠陥種別レコードを作成する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            defect_type_data (DefectType): 作成する欠陥種別データ。

        Returns:
            bool: 作成に成功した場合はTrue。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret = self._defect_type_dao.create(conn, defect_type_data)
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
        self, conn: Connection, defect_type_data: DefectType
    ) -> list[DefectType] | None:
        """欠陥種別レコードを検索・取得する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            defect_type_data (DefectType): 検索条件を含む欠陥種別データ。

        Returns:
            list[DefectType] | None: 取得された欠陥種別リスト。

        Raises:
            ValueError: 検索条件が不正な場合。
            RuntimeError: データベースエラーが発生した場合。
        """
        try:
            result: list[DefectType] = self._defect_type_dao.read(
                conn, defect_type_data)
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, defect_type_data: DefectType) -> bool:
        """欠陥種別レコードを更新する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            defect_type_data (DefectType): 検索条件および更新値を含む欠陥種別データ。

        Returns:
            bool: 更新に成功した場合はTrue、更新対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._defect_type_dao.update(conn, defect_type_data)
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

    def delete(self, conn: Connection, defect_type_data: DefectType) -> bool:
        """欠陥種別レコードを削除する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            defect_type_data (DefectType): 検索条件を含む欠陥種別データ。

        Returns:
            bool: 削除に成功した場合はTrue、削除対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._defect_type_dao.delete(conn, defect_type_data)
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
