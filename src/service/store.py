"""保管庫情報サービスモジュール。

保管庫（スロット）情報に対する照会および状態更新のビジネスロジックと
トランザクション制御を提供します。
"""

from logging import Logger

import mariadb
from mariadb import Connection

from dao import StoreDAO
from model import Store


class StoreService:
    """保管庫情報に関するビジネスロジックを処理するサービスクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
        _store_dao (StoreDAO): 保管庫DAOインスタンス。
    """

    def __init__(self, logger: Logger) -> None:
        """StoreServiceのインスタンスを初期化する。

        Args:
            logger (Logger): ロガーインスタンス。
        """
        self._logger = logger

        self._store_dao = StoreDAO(self._logger)

    def read(self, conn: Connection, store_data: Store) -> list[Store] | None:
        """保管庫レコードを検索・取得する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            store_data (Store): 検索条件を含む保管庫データ。

        Returns:
            list[Store] | None: 取得された保管庫リスト。

        Raises:
            ValueError: 検索条件が不正な場合。
            RuntimeError: データベースエラーが発生した場合。
        """
        try:
            result: list[Store] = self._store_dao.read(conn, store_data)
        except ValueError:
            raise

        except mariadb.Error as e:
            raise RuntimeError(
                "Require reboot this process (sys.exit(1))") from e

        return result

    def update(self, conn: Connection, store_data: Store) -> bool:
        """保管庫レコードを更新する。

        Args:
            conn (Connection): データベース接続オブジェクト。
            store_data (Store): 検索条件および更新値を含む保管庫データ。

        Returns:
            bool: 更新に成功した場合はTrue、更新対象がなかった場合はFalse。

        Raises:
            ValueError: 入力データが不正な場合。
            RuntimeError: データベースエラーが発生した場合（ロールバック後に発生）。
        """
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
