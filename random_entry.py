# random_entry.py
import sqlite3
import random
from typing import Optional, Dict

class _RandomPicker:
    """内部伪随机选择器，每次返回字典 {'content': ..., 'extra': ...}"""

    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._used_ids: set = set()
        self._all_ids: set = self._load_all_ids()
        self._last_entry_count = len(self._all_ids)

    def _load_all_ids(self) -> set:
        try:
            cur = self._conn.execute("SELECT id FROM entries")
            return {row[0] for row in cur}
        except Exception:
            return set()

    def pick(self) -> Optional[Dict[str, str]]:
        available = self._all_ids - self._used_ids
        if not available:
            self._used_ids.clear()
            available = self._all_ids.copy()

        if not available:
            return None

        chosen_id = random.choice(list(available))
        self._used_ids.add(chosen_id)

        try:
            cur = self._conn.execute(
                "SELECT content, COALESCE(extra, '') FROM entries WHERE id = ?",
                (chosen_id,)
            )
            row = cur.fetchone()
            if row:
                return {'content': row[0], 'extra': row[1]}
        except Exception:
            pass
        return None

    def refresh_if_needed(self, entry_count: int):
        if entry_count != self._last_entry_count:
            self._all_ids = self._load_all_ids()
            self._used_ids.clear()
            self._last_entry_count = len(self._all_ids)


_pickers: Dict[int, _RandomPicker] = {}

def get_random_entry(conn: sqlite3.Connection, entry_count: int) -> Optional[Dict[str, str]]:
    """
    伪随机获取一条记录，返回字典 {'content': ..., 'extra': ...}。
    若无数据或未连接返回 None。
    """
    if not conn or entry_count == 0:
        return None

    key = id(conn)
    if key not in _pickers:
        _pickers[key] = _RandomPicker(conn)
    picker = _pickers[key]
    picker.refresh_if_needed(entry_count)
    return picker.pick()