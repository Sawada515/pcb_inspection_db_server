"""基板検査情報 (inspection_tb) データアクセスモジュール。

検査結果情報の登録、取得、更新、削除を行うDAOクラスを提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from model import Inspection


class InspectionDAO:
    """検査テーブル (inspection_tb) に対するCRUD操作を提供するDAOクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _table_name (str): テーブル名 (inspection_tb)。
    """

    def __init__(self, logger: Logger):
        """InspectionDAOのインスタンスを初期化する。

        Args:
            logger (Logger): ロギングに使用するロガー。
        """
        self._logger = logger

        self._table_name = "inspection_tb"

        self._create_required_fields = [
            "inspection_id",
            "user_id",
        ]

        self._read_search_white_list = [
            "inspection_id",
            "top_image_path",
            "bottom_image_path",
            "user_id",
        ]

        self._update_search_white_list = [
            "inspection_id",
            "user_id",
        ]
        self._update_white_list = [
            "finished_at",
            "top_image_path",
            "bottom_image_path",
            "feedback",
        ]

        self._delete_search_white_list = [
            "inspection_id",
            "user_id",
        ]

    def create(self, conn: Connection, inspection_data: Inspection) -> bool:
        """新しい検査レコードをデータベースに作成する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            inspection_data (Inspection): 登録する検査データ。

        Returns:
            bool: 登録が成功した場合はTrue。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または必須フィールドが不足している場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if inspection_data is None:
            raise ValueError("Inspection data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}"
            )
            raise

        for field in self._create_required_fields:
            if getattr(inspection_data, field, None) is None:
                self._logger.error(
                    f"{self.__class__.__name__}: Missing required field: {field}"
                )
                raise ValueError(f"Missing required field: {field}")

        query = f"""
            INSERT INTO {self._table_name} (
                `inspection_id`,
                `started_at`,
                `finished_at`,
                `top_image_path`,
                `bottom_image_path`,
                `feedback`,
                `user_id`,
                `created_at`,
                `updated_at`
            ) VALUES (?, ?, ?, ?, ?, ?, ?, NOW(), NOW())
        """

        try:
            cursor.execute(
                query,
                (
                    inspection_data.inspection_id,
                    inspection_data.started_at,
                    inspection_data.finished_at,
                    inspection_data.top_image_path,
                    inspection_data.bottom_image_path,
                    inspection_data.feedback,
                    inspection_data.user_id,
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

    def read(self, conn: Connection, inspection_data: Inspection) -> list[Inspection]:
        """検索条件に一致する検査レコードを取得する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            inspection_data (Inspection): 検索条件を含む検査データ。

        Returns:
            list[Inspection]: 取得された検査オブジェクトのリスト。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if inspection_data is None:
            raise ValueError("Inspection data is None")

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
            value = getattr(inspection_data, key, None)
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
            `inspection_id`,
            `started_at`,
            `finished_at`,
            `top_image_path`,
            `bottom_image_path`,
            `feedback`,
            `user_id`
        FROM
            {self._table_name}
        WHERE {' AND '.join(search_conditions)}
        """

        try:
            cursor.execute(query, tuple(search_values))

            results: list[Inspection] = []
            for r in cursor.fetchall():
                inspection = Inspection(
                    inspection_id=r[0],
                    started_at=r[1],
                    finished_at=r[2],
                    top_image_path=r[3],
                    bottom_image_path=r[4],
                    feedback=r[5],
                    user_id=r[6],
                )
                results.append(inspection)

            return results
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def update(self, conn: Connection, inspection_data: Inspection) -> bool:
        """指定された検索条件に一致する検査レコードを更新する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            inspection_data (Inspection): 検索条件および更新値を含む検査データ。

        Returns:
            bool: 1行以上更新された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件/更新条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if inspection_data is None:
            raise ValueError("Inspection data is None")

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
            value = getattr(inspection_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value
                )

        for key in self._update_white_list:
            value = getattr(inspection_data, key, None)
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

    def delete(self, conn: Connection, inspection_data: Inspection) -> bool:
        """指定された検索条件に一致する検査レコードを削除する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            inspection_data (Inspection): 検索条件を含む検査データ。

        Returns:
            bool: 1行以上削除された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if inspection_data is None:
            raise ValueError("Inspection data is None")

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
            value = getattr(inspection_data, key, None)
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
