import sqlite3
from DapsEX.payload import Settings
from contextlib import closing


class Database:
    def __init__(self) -> None:
        self.initialize_db()

    def get_db_connection(self):
        conn = sqlite3.connect(Settings.DB_PATH.value)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_db(self):
        with self.get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    """
                CREATE TABLE IF NOT EXISTS file_cache (
                    file_path text PRIMARY KEY,
                    file_hash TEXT UNIQUE,
                    source_path TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
                )
                conn.commit()

    def add_file(self, file_path: str, file_hash: str, source_path: str) -> None:
        with self.get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "INSERT OR IGNORE INTO file_cache (file_path, file_hash, source_path) VALUES (?, ?, ?)",
                    (file_path, file_hash, source_path)
                )
            conn.commit()

    def update_file(self, file_hash: str, source_path: str, file_path: str) -> None:
        with self.get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "UPDATE file_cache SET file_hash = ?, source_path = ? WHERE file_path = ?",
                    (file_hash, source_path, file_path)
                )
            conn.commit()

    def get_cached_file(self, file_path: str) -> dict[str, str] | None:
        with self.get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "SELECT * FROM file_cache WHERE file_path = ?",
                    (file_path,)
                )
                result = cursor.fetchone()
                if result:
                    return dict(result)
                else:
                    return None
    
    def delete_cached_file(self, file_path: str) -> None:
        with self.get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute(
                    "DELETE FROM file_cache WHERE file_path = ?",
                    (file_path,)
                )
                conn.commit()

    def return_all_files(self) -> dict[str, dict]:
        with self.get_db_connection() as conn:
            with closing(conn.cursor()) as cursor:
                cursor.execute("SELECT * FROM file_cache")
                result = cursor.fetchall()
                return {
                    file_path: {
                        'file_hash': file_hash,
                        'source_path': source_path,
                        'timestamp': timestamp
                    }
                    for file_path, file_hash, source_path, timestamp, in result
                }
