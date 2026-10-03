"""検査要求情報 (inspection_request_tb) データアクセスモジュール。

検査要求の登録、取得、更新、削除を行うDAOクラスを提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from model import InspectionRequest, InspectionRequestStatus


class InspectionRequestDAO:
    """検査要求テーブル (inspection_request_tb) に対するCRUD操作を提供するDAOクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _table_name (str): テーブル名 (inspection_request_tb)。
    """

    def __init__(self, logger: Logger):
        """InspectionRequestDAOのインスタンスを初期化する。

        Args:
            logger (Logger): ロギングに使用するロガー。
        """
        self._logger = logger

        self._table_name = "inspection_request_tb"

        self._create_required_fields = [
            "request_status",
        ]

        self._read_search_white_list = [
            "request_id",
            "request_status",
        ]

        self._update_search_white_list = [
            "request_id",
            "request_status",
        ]
        self._update_white_list = [
            "request_status",
        ]

        self._delete_search_white_list = [
            "request_id",
            "request_status",
        ]

    def create(self, conn: Connection, request_data: InspectionRequest) -> bool:
        """新しい検査要求レコードをデータベースに作成する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            request_data (InspectionRequest): 登録する検査要求データ。

        Returns:
            bool: 登録が成功した場合はTrue。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または必須フィールドが不足している場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if request_data is None:
            raise ValueError("InspectionRequest data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}"
            )
            raise

        for field in self._create_required_fields:
            if getattr(request_data, field, None) is None:
                self._logger.error(
                    f"{self.__class__.__name__}: Missing required field: {field}"
                )
                raise ValueError(f"Missing required field: {field}")

        query = f"""
            INSERT INTO {self._table_name} (
                `request_status`,
                `created_at`,
                `updated_at`
            ) VALUES (?, NOW(), NOW())
        """

        print(query)

        try:
            cursor.execute(
                query,
                (
                    request_data.request_id,
                    request_data.request_status.value
                    if request_data.request_status
                    else None,
                ),
            )
            return True
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def read(
        self, conn: Connection, request_data: InspectionRequest
    ) -> list[InspectionRequest]:
        """検索条件に一致する最新の検査要求レコードを取得する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            request_data (InspectionRequest): 検索条件を含む検査要求データ。

        Returns:
            list[InspectionRequest]: 取得された検査要求オブジェクトのリスト（最大1件）。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if request_data is None:
            raise ValueError("InspectionRequest data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}"
            )
            raise

        search_conditions = []
        search_values = []

        for key in self._read_search_white_list:
            value = getattr(request_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value
                )

        if not search_conditions:
            self._logger.warning(
                f"{self.__class__.__name__}: No search conditions provided"
            )
            raise ValueError("No search conditions provided")

        query = f"""
        SELECT
            `request_id`,
            `request_status`
        FROM
            {self._table_name}
        WHERE {' AND '.join(search_conditions)}
        ORDER
            BY `created_at` DESC
        LIMIT 1
        """

        try:
            cursor.execute(query, tuple(search_values))

            results: list[InspectionRequest] = []
            for r in cursor.fetchall():
                # DB文字列値から InspectionRequestStatus Enum へ復元
                status_val = r[1]
                if status_val is not None:
                    try:
                        status = InspectionRequestStatus(status_val)
                    except ValueError:
                        status = status_val
                else:
                    status = None

                inspection_request = InspectionRequest(
                    request_id=r[0],
                    request_status=status,
                )
                results.append(inspection_request)

            return results
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def update(self, conn: Connection, request_data: InspectionRequest) -> bool:
        """指定された検索条件に一致する検査要求レコードを更新する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            request_data (InspectionRequest): 検索条件および更新値を含む検査要求データ。

        Returns:
            bool: 1行以上更新された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件/更新条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if request_data is None:
            raise ValueError("InspectionRequest data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}"
            )
            raise

        search_conditions = []
        search_values = []
        update_conditions = []
        update_values = []

        for key in self._update_search_white_list:
            value = getattr(request_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value
                )

        for key in self._update_white_list:
            value = getattr(request_data, key, None)
            if value is not None:
                update_conditions.append(f"`{key}` = ?")
                update_values.append(
                    value.value if hasattr(value, "value") else value
                )

        if not search_conditions:
            self._logger.warning(
                f"{self.__class__.__name__}: No search conditions provided"
            )
            raise ValueError("No search conditions provided")

        if not update_conditions:
            self._logger.warning(
                f"{self.__class__.__name__}: No update conditions provided"
            )
            raise ValueError("No update conditions provided")

        query = f"""
        UPDATE
            {self._table_name}
        SET {', '.join(update_conditions)}, `updated_at` = NOW()
        WHERE {' AND '.join(search_conditions)}
        """

        try:
            cursor.execute(query, tuple(update_values + search_values))
            return cursor.rowcount > 0
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def delete(self, conn: Connection, request_data: InspectionRequest) -> bool:
        """指定された検索条件に一致する検査要求レコードを削除する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            request_data (InspectionRequest): 検索条件を含む検査要求データ。

        Returns:
            bool: 1行以上削除された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if request_data is None:
            raise ValueError("InspectionRequest data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}"
            )
            raise

        search_conditions = []
        search_values = []

        for key in self._delete_search_white_list:
            value = getattr(request_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value
                )

        if not search_conditions:
            self._logger.warning(
                f"{self.__class__.__name__}: No search conditions provided"
            )
            raise ValueError("No search conditions provided")

        query = f"""
        DELETE
        FROM
            {self._table_name}
        WHERE {' AND '.join(search_conditions)}
        """

        try:
            cursor.execute(query, tuple(search_values))
            return cursor.rowcount > 0
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
            raise
        finally:
            if cursor is not None:
                cursor.close()
