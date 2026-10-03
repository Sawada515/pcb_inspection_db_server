"""データベース接続管理モジュール。

MariaDBのConnectionPoolを利用してデータベース接続の取得と返却を管理します。
"""

import mariadb
from mariadb import Connection


class DatabaseConnector:
    """MariaDB接続プールを管理し、接続の貸出・返却を提供するクラス。

    Attributes:
        pool (mariadb.ConnectionPool): MariaDB接続プールインスタンス。
    """

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """DatabaseConnectorのインスタンスを初期化し、接続プールを作成する。

        Args:
            host (str): データベースホスト名またはIPアドレス。
            port (int): ポート番号。
            user (str): 接続ユーザー名。
            password (str): 接続パスワード。
            database (str): データベース名。
        """
        self.pool = mariadb.ConnectionPool(
            pool_name="inspection_system_pool",
            pool_size=5,
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )

    def get_connection(self) -> Connection:
        """接続プールからアクティブなデータベース接続を取得する。

        Returns:
            Connection: MariaDBデータベース接続オブジェクト。

        Raises:
            RuntimeError: データベース接続の取得に失敗した場合。
        """
        try:
            return self.pool.get_connection()
        except mariadb.Error as e:
            raise RuntimeError(f"Error connecting to the database: {e}")

    def release_connection(self, conn: Connection) -> None:
        """使用済みのデータベース接続をプールに返却する。

        Args:
            conn (Connection): 返却するMariaDBデータベース接続オブジェクト。
        """
        if conn:
            conn.close()

