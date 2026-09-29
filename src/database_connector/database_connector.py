import mariadb
from mariadb import Connection


class DatabaseConnector:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
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
        try:
            return self.pool.get_connection()
        except mariadb.Error as e:
            raise RuntimeError(f"Error connecting to the database: {e}")

    def release_connection(self, conn: Connection) -> None:
        if conn:
            conn.close()
