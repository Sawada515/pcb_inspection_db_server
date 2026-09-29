from logging import Logger

import mariadb
from mariadb import Connection

from dao import StoreDAO
from model import Store


class StoreService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger

        self._store_dao = StoreDAO(self._logger)

    def read(self, conn: Connection, store_data: Store) -> list[Store] | None:
        try:
            result: list[Store] = self._store_dao.read(conn, store_data)
        except ValueError:
            raise

        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, store_data: Store) -> bool:
        try:
            ret: bool = self._store_dao.update(conn, store_data)
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
