"""複雑なデータ操作を行うDAOクラスを提供します。"""

from logging import Logger

import mariadb
from mariadb import Connection

from src.model import *


class ComplexDAO:
    """複雑なデータ操作を行うDAOクラス。

    Attributes:
        _logger (Logger): ロガーインスタンス。
    """

    def __init__(self, logger: Logger):
        """ComplexDAOのインスタンスを初期化する。

        Args:
            logger (Logger): ロギングに使用するロガー。
        """
        self._logger = logger
        
    
    def get_user_list(self, conn: Connection) -> list[UserList]:
        """ユーザーリストを取得する。

        Args:
            conn (Connection): MariaDBデータベース接続オブジェクト。

        Returns:
            List[UserList]: 取得されたユーザーリストオブジェクトのリスト。
        """
        if conn is None:
            raise ValueError("Database connection is None")
        
        cursor = None
        
        try:
            cursor = conn.cursor()
        except mariadb.Error as e:
            self._logger.error(f"Failed to create cursor: {e}")

            raise

        query = """
        SELECT
            u.user_id,
            u.created_at,
            i.final_inspection_at
        FROM
            user_tb u
        LEFT JOIN (
            SELECT
                user_id,
                MAX(created_at) AS final_inspection_at
            FROM
                inspection_tb
            GROUP BY
                user_id
        ) i ON u.user_id = i.user_id
        WHERE
            u.user_status = 'active'
        """

        try:
            cursor.execute(query)

            results: list[UserList] = []
            
            for r in cursor.fetchall():
                user_list = UserList(
                    username=r[0],
                    created_at=r[1],
                    final_inspection_at=r[2]
                )

                results.append(user_list)
            
            return results
        except mariadb.Error as e:
            self._logger.error(
                f"{self.__class__.__name__}: Error executing query: {e}"
            )
        
            raise
        finally:
            if cursor is not None:
                cursor.close()
