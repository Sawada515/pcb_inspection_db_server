
from logging import Logger

import mariadb
from mariadb import Connection

from model import Store, StoreStatus


class StoreDAO:
    def __init__(self, logger: Logger):
        self._table_name = "store_tb"
        self._logger = logger

        self._read_search_white_list = [
            "store_id", "col", "row", "store_status"]

        self._update_search_white_list = ["store_id", "col", "row"]
        self._update_white_list = ["store_status", "user_id"]

    def create(self, conn: Connection, store_data: Store) -> None:
        """
        このメソッドは使わない
        テーブル作成時にデータも保存済みなため
        """

        raise NotImplementedError("This method is not implemented")

    def read(self, conn: Connection, store_data: Store) -> list[Store]:
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

        print(type(store_data))
        print(f"store_data: {store_data}")

        for key in self._read_search_white_list:
            value = getattr(store_data, key, None)
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
            `store_id`,
            `col`,
            `row`,
            `store_status`,
            `user_id`
        FROM
        {self._table_name}
        WHERE {' AND '.join(search_conditions)}

        """

        print(f"Executing query: {query} with values: {search_values}")

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
        SET {' , '.join(update_conditions)}
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
        """
        このメソッドは使わない
        データ削除は絶対に行わない
        """

        raise NotImplementedError("This method is not implemented")
