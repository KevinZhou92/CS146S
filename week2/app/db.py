from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


class Database:
    """Lightweight SQLite access layer with shared helpers and schema management."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def _ensure_data_directory(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        self._ensure_data_directory()
        conn = sqlite3.connect(self._path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init(self) -> None:
        with self.connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                );
                """
            )

    def insert_note(self, content: str) -> Dict[str, Any]:
        with self.connection() as conn:
            cursor = conn.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            note_id = int(cursor.lastrowid)
            row = conn.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?", (note_id,)
            ).fetchone()
            return self._row_to_note(row)

    def list_notes(self) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT id, content, created_at FROM notes ORDER BY id DESC"
            ).fetchall()
            return [self._row_to_note(row) for row in rows]

    def get_note(self, note_id: int) -> Optional[Dict[str, Any]]:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            ).fetchone()
            return self._row_to_note(row) if row else None

    def insert_action_items(
        self, items: List[str], *, note_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if not items:
            return []
        with self.connection() as conn:
            created: List[Dict[str, Any]] = []
            for item in items:
                cursor = conn.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                action_id = int(cursor.lastrowid)
                row = conn.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                    (action_id,),
                ).fetchone()
                created.append(self._row_to_action_item(row))
            return created

    def list_action_items(self, note_id: Optional[int] = None) -> List[Dict[str, Any]]:
        with self.connection() as conn:
            if note_id is None:
                rows = conn.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                ).fetchall()
            return [self._row_to_action_item(row) for row in rows]

    def mark_action_item_done(self, action_item_id: int, done: bool) -> Optional[Dict[str, Any]]:
        with self.connection() as conn:
            conn.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )
            row = conn.execute(
                "SELECT id, note_id, text, done, created_at FROM action_items WHERE id = ?",
                (action_item_id,),
            ).fetchone()
            return self._row_to_action_item(row) if row else None

    @staticmethod
    def _row_to_note(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": int(row["id"]),
            "content": row["content"],
            "created_at": row["created_at"],
        }

    @staticmethod
    def _row_to_action_item(row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": int(row["id"]),
            "note_id": row["note_id"],
            "text": row["text"],
            "done": bool(row["done"]),
            "created_at": row["created_at"],
        }


database = Database(DB_PATH)


