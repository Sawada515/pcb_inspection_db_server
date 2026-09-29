from logging import Logger

import mariadb
from mariadb import Connection

from dao import DefectDAO
from model import Defect


class DefectService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._defect_dao = DefectDAO(self._logger)

    def create(self, conn: Connection, defect_data: Defect) -> bool:
        try:
            ret = self._defect_dao.create(conn, defect_data)
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

    def read(self, conn: Connection, defect_data: Defect) -> list[Defect] | None:
        try:
            result: list[Defect] = self._defect_dao.read(conn, defect_data)
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, defect_data: Defect) -> bool:
        try:
            ret: bool = self._defect_dao.update(conn, defect_data)
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

    def delete(self, conn: Connection, defect_data: Defect) -> bool:
        try:
            ret: bool = self._defect_dao.delete(conn, defect_data)
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
