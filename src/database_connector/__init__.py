"""データベース接続管理パッケージ。

MariaDB接続プールを管理するDatabaseConnectorクラスを提供します。
"""

from .database_connector import DatabaseConnector

__all__ = ["DatabaseConnector"]
