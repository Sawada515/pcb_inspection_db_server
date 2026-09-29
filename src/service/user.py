from logging import Logger

import mariadb
from mariadb import Connection

from dao import UserDAO
from model import User


class UserService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

        self._user_dao = UserDAO(self._logger)

    def create(self, conn: Connection, user_data: User) -> bool:
        try:
            ret = self._user_dao.create(conn, user_data)
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

    def read(self, conn: Connection, user_data: User) -> list[User] | None:
        try:
            result: list[User] = self._user_dao.read(conn, user_data)
        except ValueError:
            raise

        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, user_data: User) -> bool:
        try:
            ret: bool = self._user_dao.update(conn, user_data)
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

    def delete(self, conn: Connection, user_data: User) -> bool:
        try:
            ret: bool = self._user_dao.delete(conn, user_data)
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
