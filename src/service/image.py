"""画像情報サービスモジュール。

画像パス情報に対するCRUD操作のビジネスロジックおよびトランザクション制御を提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from src.dao import ImageDAO
from src.model import Image


class ImageService:
    """画像情報に関するビジネスロジックを処理するサービスクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _image_dao (ImageDAO): 画像情報DAOインスタンス。
    """

    def __init__(self, logger: Logger) -> None:
        """ImageServiceのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger
        self._image_dao = ImageDAO(self._logger)

    def create(self, conn: Connection, image_data: Image) -> bool:
        """画像レコードを作成する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            image_data (Image): 作成する画像データ。

        Returns:
            bool: 作成に成功した場合はTrue。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
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
        """画像レコードを検索・取得する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            image_data (Image): 検索条件を含む画像データ。

        Returns:
            list[Image] | None: 取得された画像リスト。

        Raises:
            ValueError: 検索条件が不正な場合。
            RuntimeError: データベースエラーが発生した場合。
        """
        try:
            result: list[Image] = self._image_dao.read(conn, image_data)
        except ValueError:
            raise
        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, image_data: Image) -> bool:
        """画像レコードを更新する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            image_data (Image): 検索条件および更新値を含む画像データ。

        Returns:
            bool: 更新に成功した場合はTrue、更新対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
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
        """画像レコードを削除する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            image_data (Image): 検索条件を含む画像データ。

        Returns:
            bool: 削除に成功した場合はTrue、削除対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
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
