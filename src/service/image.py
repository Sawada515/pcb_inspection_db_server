from logging import Logger

import mariadb
from mariadb import Connection

from dao import ImageDAO
from model import Image


class ImageService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger
        self._image_dao = ImageDAO(self._logger)

    def create(self, conn: Connection, image_data: Image) -> bool:
        try:
            ret = self._image_dao.create(conn, image_data)
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

    def read(self, conn: Connection, image_data: Image) -> list[Image] | None:
        try:
            result: list[Image] = self._image_dao.read(conn, image_data)
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, image_data: Image) -> bool:
        try:
            ret: bool = self._image_dao.update(conn, image_data)
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

    def delete(self, conn: Connection, image_data: Image) -> bool:
        try:
            ret: bool = self._image_dao.delete(conn, image_data)
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
