
"""保管庫情報 (store_tb) データアクセスモジュール。

保管庫（スロット）の状態取得および状態更新を行うDAOクラスを提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from src.model import Store, StoreStatus


class StoreDAO:
    """保管庫テーブル (store_tb) に対する操作を提供するDAOクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _table_name (str): テーブル名 (store_tb)。
    """

    def __init__(self, logger: Logger):
        """StoreDAOのインスタンスを初期化する。

        Args:
            logger (Logger): ロギングに使用するロガー。
        """
        self._table_name = "store_tb"
        self._logger = logger

        self._read_search_white_list = [
            "store_id", "col", "row", "store_status"]

        self._update_search_white_list = ["store_id", "col", "row"]
        self._update_white_list = ["store_status", "user_id"]

    def create(self, conn: Connection, store_data: Store) -> None:
        """新しい保管庫レコードを作成する（未実装）。

        Note:
            テーブル作成時に初期データが配置済みのため、本メソッドはサポートされません。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            store_data (Store): 保管庫データ。

        Raises:
            NotImplementedError: 本メソッドが呼び出された場合に常に発生します。
        """
        raise NotImplementedError("This method is not implemented")

    def read(self, conn: Connection, store_data: Store) -> list[Store]:
        """検索条件に一致する保管庫レコードを取得する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            store_data (Store): 検索条件を含む保管庫データ。

        Returns:
            list[Store]: 取得された保管庫オブジェクトのリスト。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または検索条件が指定されていない場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if store_data is None:
            raise ValueError("Store data is None")

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
            value = getattr(store_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value)
        
        query = ""

        if not search_conditions:
            query = f"""
            SELECT
                `store_id`,
                `col`,
                `row`,
                `store_status`,
                `user_id`
            FROM
            {self._table_name}
    
            """
        else:
            query = f"""
            SELECT
                `store_id`,
                `col`,
                `row`,
                `store_status`,
                `user_id`
            FROM
            {self._table_name}
            WHERE {' AND '.join(search_conditions)}
    
            """

        try:
            cursor.execute(query, tuple(search_values))

            results: list[Store] = []

            for r in cursor.fetchall():
                store = Store(
                    store_id=r[0],
                    col=r[1],
                    row=r[2],
                    store_status=StoreStatus(r[3]),
                    user_id=r[4]
                )
                results.append(store)

            return results
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}")

            raise
        finally:
            if cursor is not None:
                cursor.close()

    def update(self, conn: Connection, store_data: Store) -> bool:
        """指定された検索条件に一致する保管庫レコードを更新する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            store_data (Store): 検索条件（store_id または col/row）および更新値（store_status, user_id）を含む保管庫データ。

        Returns:
            bool: 1行以上更新された場合はTrue、それ以外はFalse。

        Raises:
            ValueError: 接続またはデータがNoneの場合、または必要な検索条件/更新条件が不足している場合。
            mariadb.Error: データベース操作中にエラーが発生した場合。
        """
        if conn is None:
            raise ValueError("Connection is None")
        if store_data is None:
            raise ValueError("Store data is None")

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

        if store_data.store_id is not None:
            search_conditions.append("`store_id` = ?")
            search_values.append(store_data.store_id)
        else:
            if store_data.col is not None:
                search_conditions.append("`col` = ?")
                search_values.append(store_data.col)
            else:
                self._logger.error(
                    f"{self.__class__.__name__}: Either store_id or col must be provided for search conditions")

                raise ValueError(
                    "Either store_id or col must be provided for search conditions")

            if store_data.row is not None:
                search_conditions.append("`row` = ?")
                search_values.append(store_data.row)
            else:
                self._logger.error(
                    f"{self.__class__.__name__}: Either store_id or row must be provided for search conditions")

                raise ValueError(
                    "Either store_id or row must be provided for search conditions")

        for key in self._update_white_list:
            value = getattr(store_data, key, None)
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

    def delete(self, conn: Connection, store_data: Store) -> None:
        """保管庫レコードを削除する（未実装）。

        Note:
            保管庫データの削除は仕様上行われません。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。
            store_data (Store): 保管庫データ。

        Raises:
            NotImplementedError: 本メソッドが呼び出された場合に常に発生します。
        """
        raise NotImplementedError("This method is not implemented")
