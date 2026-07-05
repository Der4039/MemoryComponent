# data_provider.py
import sqlite3

class DataProvider:
    """封装数据库基本操作，不涉及随机读取"""

    def __init__(self):
        self._conn = None
        self._db_path = None
        self._entry_count = 0

    @property
    def db_path(self):
        return self._db_path

    @property
    def entry_count(self):
        return self._entry_count

    @property
    def connection(self):
        return self._conn

    def open_database(self, file_path: str) -> bool:
        if self._conn:
            self.close()

        self._conn = sqlite3.connect(file_path)
        # 创建表（包含新字段 extra，默认为空字符串）
        self._conn.execute(
            "CREATE TABLE IF NOT EXISTS entries "
            "(id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT NOT NULL, extra TEXT DEFAULT '')"
        )
        # 兼容旧数据库：如果 extra 列不存在则添加
        self._maybe_add_extra_column()
        self._conn.commit()
        self._db_path = file_path
        self._update_entry_count()
        return True

    def _maybe_add_extra_column(self):
        """检查并添加 extra 列，用于升级旧数据库"""
        cursor = self._conn.execute("PRAGMA table_info(entries)")
        columns = [col[1] for col in cursor]
        if 'extra' not in columns:
            self._conn.execute("ALTER TABLE entries ADD COLUMN extra TEXT DEFAULT ''")
            self._conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
            self._db_path = None
            self._entry_count = 0

    def _update_entry_count(self):
        if self._conn:
            cur = self._conn.execute("SELECT COUNT(*) FROM entries")
            self._entry_count = cur.fetchone()[0]
        else:
            self._entry_count = 0

    def has_database(self) -> bool:
        return self._conn is not None

    def has_entries(self) -> bool:
        return self.has_database() and self._entry_count > 0