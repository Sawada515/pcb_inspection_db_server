from logging import Logger

import mariadb
from mariadb import Connection

from dao import InspectionDAO
from model import Inspection


class InspectionService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._inspection_dao = InspectionDAO(self._logger)

    def create(self, conn: Connection, inspection_data: Inspection) -> bool:
        try:
            ret = self._inspection_dao.create(conn, inspection_data)
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
        self, conn: Connection, inspection_data: Inspection
    ) -> list[Inspection] | None:
        try:
            result: list[Inspection] = self._inspection_dao.read(
                conn, inspection_data)
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, inspection_data: Inspection) -> bool:
        try:
            ret: bool = self._inspection_dao.update(conn, inspection_data)
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

    def delete(self, conn: Connection, inspection_data: Inspection) -> bool:
        try:
            ret: bool = self._inspection_dao.delete(conn, inspection_data)
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
