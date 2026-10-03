"""ユーザー情報 (user_tb) データアクセスモジュール。

作業者・管理者等のユーザー情報の登録、取得、更新、削除を行うDAOクラスを提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from model import User, UserRole, UserStatus


class UserDAO:
    """ユーザーテーブル (user_tb) に対するCRUD操作を提供するDAOクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _table_name (str): テーブル名 (user_tb)。
    """

    def __init__(self, logger: Logger):
        """UserDAOのインスタンスを初期化する。

        Args:
            logger (Logger): ロギングに使用するロガー。
        """
        self._logger = logger

        self._table_name = "user_tb"

        self._create_required_fields = [
            "user_id", "role", "uuid", "user_status"
        ]

        self._read_search_white_list = [
            "user_id", "role", "uuid", "user_status"
        ]

        self._update_search_white_list = [
            "user_id", "role", "uuid"
        ]
        self._update_white_list = ["user_status"]

        self._delete_search_white_list = [
            "user_id", "role", "uuid", "user_status"
        ]

    def create(self, conn: Connection, user_data: User) -> bool:
        """新しいユーザーレコードをデータベースに作成する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            user_data (User): 登録するユーザーデータ。

        Returns:
            bool: 登録が成功した場合はTrue。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または必須フィールドが不足している場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if user_data is None:
            raise ValueError("User data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}")
            raise

        query = f"""
            INSERT INTO {self._table_name} (
                `user_id`,
                `role`,
                `uuid`,
                `user_status`,
                `created_at`,
                `updated_at`
            ) VALUES (?, ?, ?, ?, NOW(), NOW())
        """
        for field in self._create_required_fields:
            if getattr(user_data, field, None) is None:
                self._logger.error(
                    f"{self.__class__.__name__}: Missing required field: {field}")
                raise ValueError(f"Missing required field: {field}")

        assert user_data.role is not None
        assert user_data.user_status is not None

        try:
            cursor.execute(query, (
                user_data.user_id,
                user_data.role.value,
                user_data.uuid,
                user_data.user_status.value,
            ))
            return True
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}")
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def read(self, conn: Connection, user_data: User) -> list[User]:
        """検索条件に一致するユーザーレコードを取得する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            user_data (User): 検索条件を含むユーザーデータ。

        Returns:
            list[User]: 取得されたユーザーオブジェクトのリスト。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if user_data is None:
            raise ValueError("User data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}")
            raise

        search_conditions = []
        search_values = []

        for key in self._read_search_white_list:
            value = getattr(user_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value)

        if not search_conditions:
            self._logger.warning(
                f"{self.__class__.__name__}: No search conditions provided")
            raise ValueError("No search conditions provided")

        query = f"""
        SELECT
            `user_id`,
            `role`,
            `uuid`,
            `user_status`
        FROM
            {self._table_name}
        WHERE {' AND '.join(search_conditions)}
        """

        try:
            cursor.execute(query, tuple(search_values))

            results: list[User] = []
            for r in cursor.fetchall():
                # DB値から Enum へ変換して復元
                user = User(
                    user_id=r[0],
                    role=UserRole(r[1]) if "UserRole" in globals(
                    ) and isinstance(UserRole, type) else r[1],
                    uuid=r[2],
                    user_status=UserStatus(r[3]) if "UserStatus" in globals(
                    ) and isinstance(UserStatus, type) else r[3]
                )
                results.append(user)

            return results
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}")
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def update(self, conn: Connection, user_data: User) -> bool:
        """指定された検索条件に一致するユーザーレコードを更新する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            user_data (User): 検索条件および更新値を含むユーザーデータ。

        Returns:
            bool: 1行以上更新された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件/更新条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if user_data is None:
            raise ValueError("User data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}")
            raise

        search_conditions = []
        search_values = []
        update_conditions = []
        update_values = []

        for key in self._update_search_white_list:
            value = getattr(user_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value)

        for key in self._update_white_list:
            value = getattr(user_data, key, None)
            if value is not None:
                update_conditions.append(f"`{key}` = ?")
                update_values.append(
                    value.value if hasattr(value, "value") else value)

        if not search_conditions:
            self._logger.warning(
                f"{self.__class__.__name__}: No search conditions provided")
            raise ValueError("No search conditions provided")

        if not update_conditions:
            self._logger.warning(
                f"{self.__class__.__name__}: No update conditions provided")
            raise ValueError("No update conditions provided")

        query = f"""
        UPDATE
            {self._table_name}
        SET {', '.join(update_conditions)}, `updated_at` = NOW()
        WHERE {' AND '.join(search_conditions)}
        """

        print(f"user_service update query: {query}")

        try:
            cursor.execute(query, tuple(update_values + search_values))
            return cursor.rowcount > 0
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}")
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def delete(self, conn: Connection, user_data: User) -> bool:
        """指定された検索条件に一致するユーザーレコードを削除する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            user_data (User): 検索条件を含むユーザーデータ。

        Returns:
            bool: 1行以上削除された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if user_data is None:
            raise ValueError("User data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}")
            raise

        search_conditions = []
        search_values = []

        for key in self._delete_search_white_list:
            value = getattr(user_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value)

        if not search_conditions:
            self._logger.warning(
                f"{self.__class__.__name__}: No search conditions provided")
            raise ValueError("No search conditions provided")

        query = f"""
        DELETE
        FROM
            {self._table_name}
        WHERE {' AND '.join(search_conditions)}
        """

        try:
            # search_conditions ではなく search_values を渡す
            cursor.execute(query, tuple(search_values))
            return cursor.rowcount > 0
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}")
            raise
        finally:
            if cursor is not None:
                cursor.close()
