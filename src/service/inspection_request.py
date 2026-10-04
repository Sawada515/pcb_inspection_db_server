"""検査要求情報サービスモジュール。

検査要求に対するCRUD操作のビジネスロジックおよびトランザクション制御を提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from src.dao import InspectionRequestDAO
from src.model import InspectionRequest


class InspectionRequestService:
    """検査要求に関するビジネスロジックを処理するサービスクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _inspection_request_dao (InspectionRequestDAO): 検査要求DAOインスタンス。
    """

    def __init__(self, logger: Logger) -> None:
        """InspectionRequestServiceのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger
        self._inspection_request_dao = InspectionRequestDAO(self._logger)

    def create(
        self, conn: Connection, inspection_request_data: InspectionRequest
    ) -> bool:
        """検査要求レコードを作成する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            inspection_request_data (InspectionRequest): 作成する検査要求データ。

        Returns:
            bool: 作成に成功した場合はTrue。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret = self._inspection_request_dao.create(
                conn, inspection_request_data)
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
        self, conn: Connection, inspection_request_data: InspectionRequest
    ) -> list[InspectionRequest] | None:
        """検査要求レコードを検索・取得する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            inspection_request_data (InspectionRequest): 検索条件を含む検査要求データ。

        Returns:
            list[InspectionRequest] | None: 取得された検査要求リスト（最新1件）。

        Raises:
            ValueError: 検索条件が不正な場合。
            RuntimeError: データベースエラーが発生した場合。
        """
        try:
            result: list[InspectionRequest] = self._inspection_request_dao.read(
                conn, inspection_request_data
            )
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(
        self, conn: Connection, inspection_request_data: InspectionRequest
    ) -> bool:
        """検査要求レコードを更新する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            inspection_request_data (InspectionRequest): 検索条件および更新値を含む検査要求データ。

        Returns:
            bool: 更新に成功した場合はTrue、更新対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._inspection_request_dao.update(
                conn, inspection_request_data
            )
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

    def delete(
        self, conn: Connection, inspection_request_data: InspectionRequest
    ) -> bool:
        """検査要求レコードを削除する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            inspection_request_data (InspectionRequest): 検索条件を含む検査要求データ。

        Returns:
            bool: 削除に成功した場合はTrue、削除対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
        try:
            ret: bool = self._inspection_request_dao.delete(
                conn, inspection_request_data
            )
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
