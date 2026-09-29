from logging import Logger

import mariadb
from mariadb import Connection

from model import InspectionRequest, InspectionRequestStatus


class InspectionRequestDAO:
    def __init__(self, logger: Logger):
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
