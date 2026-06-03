from contextlib import contextmanager

from config.db_config import get_db_config

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
except ImportError:
    mysql = None

    class MySQLError(Exception):
        pass


class DatabaseError(Exception):
    pass


class Database:
    def __init__(self, config: dict | None = None):
        self.config = config or get_db_config()

    def connect(self):
        if mysql is None:
            raise DatabaseError(
                "Falta mysql-connector-python. Instala dependencias con: "
                "pip install -r requirements.txt"
            )
        try:
            return mysql.connector.connect(**self.config)
        except MySQLError as exc:
            raise DatabaseError(f"No fue posible conectar con MySQL: {exc}") from exc

    @contextmanager
    def cursor(self, commit: bool = False, dictionary: bool = True):
        conn = None
        cur = None
        try:
            conn = self.connect()
            cur = conn.cursor(dictionary=dictionary)
            yield cur
            if commit:
                conn.commit()
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if cur:
                cur.close()
            if conn and conn.is_connected():
                conn.close()

    def fetch_all(self, query: str, params: tuple | None = None) -> list[dict]:
        with self.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchall()

    def fetch_one(self, query: str, params: tuple | None = None) -> dict | None:
        with self.cursor() as cur:
            cur.execute(query, params or ())
            return cur.fetchone()

    def execute(self, query: str, params: tuple | None = None) -> int:
        with self.cursor(commit=True) as cur:
            cur.execute(query, params or ())
            return cur.lastrowid

