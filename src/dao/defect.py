from logging import Logger

import mariadb
from mariadb import Connection

from model import BoardSide, Defect


class DefectDAO:
    def __init__(self, logger: Logger):
        self._logger = logger

        self._table_name = "defect_tb"

        self._create_required_fields = [
            "board_side",
            "point",
            "area",
            "defect_type_id",
            "inspection_id",
        ]

        self._read_search_white_list = [
            "defect_id",
            "board_side",
            "area",
            "defect_type_id",
            "inspection_id",
        ]

        self._update_search_white_list = [
            "defect_id",
            "board_side",
            "defect_type_id",
            "inspection_id",
        ]
        self._update_white_list = [
            "board_side",
            "point",
            "area",
            "defect_type_id",
        ]

        self._delete_search_white_list = [
            "defect_id",
            "board_side",
            "defect_type_id",
            "inspection_id",
        ]

    def create(self, conn: Connection, defect_data: Defect) -> bool:
        if conn is None:
            raise ValueError("Connection is None")
        if defect_data is None:
            raise ValueError("Defect data is None")

        cursor = None
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error creating cursor: {e}"
            )
            raise

        for field in self._create_required_fields:
            if getattr(defect_data, field, None) is None:
                self._logger.error(
                    f"{self.__class__.__name__}: Missing required field: {field}"
                )
                raise ValueError(f"Missing required field: {field}")

        query = f"""
            INSERT INTO {self._table_name} (
                `board_side`,
                `point`,
                `area`,
                `defect_type_id`,
                `inspection_id`,
                `created_at`,
                `updated_at`
            ) VALUES (?, ?, ?, ?, ?, NOW(), NOW())
        """

        try:
            cursor.execute(
                query,
                (
                    defect_data.defect_id,
                    defect_data.board_side.value
                    if defect_data.board_side
                    else None,
                    defect_data.point,
                    defect_data.area,
                    defect_data.defect_type_id,
                    defect_data.inspection_id,
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

    def read(self, conn: Connection, defect_data: Defect) -> list[Defect]:
        if conn is None:
            raise ValueError("Connection is None")
        if defect_data is None:
            raise ValueError("Defect data is None")

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
            value = getattr(defect_data, key, None)
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
            `defect_id`,
            `board_side`,
            `point`,
            `area`,
            `defect_type_id`,
            `inspection_id`
        FROM
            {self._table_name}
        WHERE {' AND '.join(search_conditions)}
        """

        try:
            cursor.execute(query, tuple(search_values))

            results: list[Defect] = []
            for r in cursor.fetchall():
                side_val = r[1]
                if side_val is not None:
                    try:
                        board_side = BoardSide(side_val)
                    except ValueError:
                        board_side = side_val
                else:
                    board_side = None

                defect = Defect(
                    defect_id=r[0],
                    board_side=board_side,
                    point=r[2],
                    area=r[3],
                    defect_type_id=r[4],
                    inspection_id=r[5],
                )
                results.append(defect)

            return results
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
            raise
        finally:
            if cursor is not None:
                cursor.close()

    def update(self, conn: Connection, defect_data: Defect) -> bool:
        if conn is None:
            raise ValueError("Connection is None")
        if defect_data is None:
            raise ValueError("Defect data is None")

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
            value = getattr(defect_data, key, None)
            if value is not None:
                search_conditions.append(f"`{key}` = ?")
                search_values.append(
                    value.value if hasattr(value, "value") else value
                )

        for key in self._update_white_list:
            value = getattr(defect_data, key, None)
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

    def delete(self, conn: Connection, defect_data: Defect) -> bool:
        if conn is None:
            raise ValueError("Connection is None")
        if defect_data is None:
            raise ValueError("Defect data is None")

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
            value = getattr(defect_data, key, None)
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
