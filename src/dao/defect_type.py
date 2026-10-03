"""欠陥種別マスタ (defect_type_tb) データアクセスモジュール。

欠陥種別の登録、取得、更新、削除を行うDAOクラスを提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from model import DefectType


class DefectTypeDAO:
    """欠陥種別テーブル (defect_type_tb) に対するCRUD操作を提供するDAOクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _table_name (str): テーブル名 (defect_type_tb)。
    """

    def __init__(self, logger: Logger):
        """DefectTypeDAOのインスタンスを初期化する。

        Args:
            logger (Logger): ロギングに使用するロガー。
        """
        self._logger = logger

        self._table_name = "defect_type_tb"

        self._create_required_fields = [
            "defect_type_id",
            "defect_type",
        ]

        self._read_search_white_list = [
            "defect_type_id",
            "defect_type",
        ]

        self._update_search_white_list = [
            "defect_type_id",
            "defect_type",
        ]
        self._update_white_list = [
            "defect_type",
        ]

        self._delete_search_white_list = [
            "defect_type_id",
            "defect_type",
        ]

    def create(self, conn: Connection, defect_type_data: DefectType) -> bool:
        """新しい欠陥種別レコードをデータベースに作成する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            defect_type_data (DefectType): 登録する欠陥種別データ。

        Returns:
            bool: 登録が成功した場合はTrue。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または必須フィールドが不足している場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if defect_type_data is None:
            raise ValueError("DefectType data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}"
            )
            raise

        for field in self._create_required_fields:
            if getattr(defect_type_data, field, None) is None:
                self._logger.error(
                    f"{self.__class__.__name__}: Missing required field: {field}"
                )
                raise ValueError(f"Missing required field: {field}")

        query = f"""
            INSERT INTO {self._table_name} (
                `defect_type_id`,
                `defect_type`,
                `created_at`,
                `updated_at`
            ) VALUES (?, ?, NOW(), NOW())
        """

        try:
            cursor.execute(
                query,
                (
                    defect_type_data.defect_type_id,
                    defect_type_data.defect_type,
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
        self, conn: Connection, defect_type_data: DefectType
    ) -> list[DefectType]:
        """検索条件に一致する欠陥種別レコードを取得する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            defect_type_data (DefectType): 検索条件を含む欠陥種別データ。

        Returns:
            list[DefectType]: 取得された欠陥種別オブジェクトのリスト。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if defect_type_data is None:
            raise ValueError("DefectType data is None")

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
            value = getattr(defect_type_data, key, None)
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
            `defect_type_id`,
            `defect_type`
        FROM
            {self._table_name}
        WHERE {' AND '.join(search_conditions)}
        """

        try:
            cursor.execute(query, tuple(search_values))

            results: list[DefectType] = []
            for r in cursor.fetchall():
                defect_type = DefectType(
                    defect_type_id=r[0],
                    defect_type=r[1],
                )
                results.append(defect_type)

            return results
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def update(
        self, conn: Connection, defect_type_data: DefectType
    ) -> bool:
        """指定された検索条件に一致する欠陥種別レコードを更新する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            defect_type_data (DefectType): 検索条件および更新値を含む欠陥種別データ。

        Returns:
            bool: 1行以上更新された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件/更新条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if defect_type_data is None:
            raise ValueError("DefectType data is None")

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
            value = getattr(defect_type_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value
                )

        for key in self._update_white_list:
            value = getattr(defect_type_data, key, None)
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

    def delete(
        self, conn: Connection, defect_type_data: DefectType
    ) -> bool:
        """指定された検索条件に一致する欠陥種別レコードを削除する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            defect_type_data (DefectType): 検索条件を含む欠陥種別データ。

        Returns:
            bool: 1行以上削除された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if defect_type_data is None:
            raise ValueError("DefectType data is None")

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
            value = getattr(defect_type_data, key, None)
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
