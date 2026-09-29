from logging import Logger

import mariadb
from mariadb import Connection

from dao import DefectTypeDAO
from model import DefectType


class DefectTypeService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._defect_type_dao = DefectTypeDAO(self._logger)

    def create(self, conn: Connection, defect_type_data: DefectType) -> bool:
        try:
            ret = self._defect_type_dao.create(conn, defect_type_data)
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
        self, conn: Connection, defect_type_data: DefectType
    ) -> list[DefectType] | None:
        try:
            result: list[DefectType] = self._defect_type_dao.read(
                conn, defect_type_data)
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, defect_type_data: DefectType) -> bool:
        try:
            ret: bool = self._defect_type_dao.update(conn, defect_type_data)
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

    def delete(self, conn: Connection, defect_type_data: DefectType) -> bool:
        try:
            ret: bool = self._defect_type_dao.delete(conn, defect_type_data)
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
