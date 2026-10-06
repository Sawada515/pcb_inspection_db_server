"""画像情報 (image_tb) データアクセスモジュール。

欠陥画像のパス情報の登録、取得、更新、削除を行うDAOクラスを提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from src.model import Image


class ImageDAO:
    """画像テーブル (image_tb) に対するCRUD操作を提供するDAOクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _table_name (str): テーブル名 (image_tb)。
    """

    def __init__(self, logger: Logger):
        """ImageDAOのインスタンスを初期化する。

        Args:
            logger (Logger): ロギングに使用するロガー。
        """
        self._logger = logger

        self._table_name = "image_tb"

        self._create_required_fields = [
            "defect_id",
            "defect_image_path",
        ]

        self._read_search_white_list = [
            "image_id",
            "defect_id",
            "defect_image_path",
        ]

        self._update_search_white_list = [
            "image_id",
            "defect_id",
        ]
        self._update_white_list = [
            "defect_image_path",
        ]

        self._delete_search_white_list = [
            "image_id",
            "defect_id",
            "defect_image_path",
        ]

    def create(self, conn: Connection, image_data: Image) -> bool:
        """新しい画像レコードをデータベースに作成する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            image_data (Image): 登録する画像データ。

        Returns:
            bool: 登録が成功した場合はTrue。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または必須フィールドが不足している場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if image_data is None:
            raise ValueError("Image data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}"
            )
            raise

        for field in self._create_required_fields:
            if getattr(image_data, field, None) is None:
                self._logger.error(
                    f"{self.__class__.__name__}: Missing required field: {field}"
                )
                raise ValueError(f"Missing required field: {field}")

        query = f"""
            INSERT INTO {self._table_name} (
                `defect_id`,
                `defect_image_path`,
                `created_at`,
                `updated_at`
            ) VALUES (?, ?, NOW(), NOW())
        """

        try:
            cursor.execute(
                query,
                (
                    image_data.defect_id,
                    image_data.defect_image_path,
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

    def read(self, conn: Connection, image_data: Image) -> list[Image]:
        """検索条件に一致する画像レコードを取得する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            image_data (Image): 検索条件を含む画像データ。

        Returns:
            list[Image]: 取得された画像オブジェクトのリスト。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if image_data is None:
            raise ValueError("Image data is None")

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
            value = getattr(image_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value
                )
        
        query = ""

        if not search_conditions:
            query = f"""
            SELECT
                `image_id`,
                `defect_id`,
                `defect_image_path`
            FROM
                {self._table_name}
            """
        else:
            query = f"""
            SELECT
                `image_id`,
                `defect_id`,
                `defect_image_path`
            FROM
                {self._table_name}
            WHERE {' AND '.join(search_conditions)}
            """

        try:
            cursor.execute(query, tuple(search_values))

            results: list[Image] = []
            for r in cursor.fetchall():
                image = Image(
                    image_id=r[0],
                    defect_id=r[1],
                    defect_image_path=r[2],
                )
                results.append(image)

            return results
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def update(self, conn: Connection, image_data: Image) -> bool:
        """指定された検索条件に一致する画像レコードを更新する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            image_data (Image): 検索条件および更新値を含む画像データ。

        Returns:
            bool: 1行以上更新された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件/更新条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if image_data is None:
            raise ValueError("Image data is None")

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
            value = getattr(image_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value
                )

        for key in self._update_white_list:
            value = getattr(image_data, key, None)
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

    def delete(self, conn: Connection, image_data: Image) -> bool:
        """指定された検索条件に一致する画像レコードを削除する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            image_data (Image): 検索条件を含む画像データ。

        Returns:
            bool: 1行以上削除された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if image_data is None:
            raise ValueError("Image data is None")

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
            value = getattr(image_data, key, None)
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
