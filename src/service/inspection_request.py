from logging import Logger

import mariadb
from mariadb import Connection

from dao import InspectionRequestDAO
from model import InspectionRequest


class InspectionRequestService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._inspection_request_dao = InspectionRequestDAO(self._logger)

    def create(
        self, conn: Connection, inspection_request_data: InspectionRequest
    ) -> bool:
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
