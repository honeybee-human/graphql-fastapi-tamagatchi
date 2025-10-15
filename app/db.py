import sqlite3
import json
import os

DB_PATH = "game.db"


def get_connection():
    """Return a SQLite3 connection with Row factory enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db_and_migrate_json_users(json_path: str = "game_data.json"):
    """
    Initialize the SQLite database and migrate users from JSON if the DB is empty.

    - Creates the `users` table if it does not exist.
    - If `users` table is empty and JSON contains users, migrates them.
    - After migration, rewrites JSON without `users` to avoid storing password hashes.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                mouse_x REAL DEFAULT 0.0,
                mouse_y REAL DEFAULT 0.0,
                is_online INTEGER DEFAULT 0,
                difficulty REAL DEFAULT 1.0
            )
            """
        )
        conn.commit()

        # If DB is empty, try migrating from JSON
        cur.execute("SELECT COUNT(*) AS count FROM users")
        count = int(cur.fetchone()["count"])

        if count == 0 and os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    data = json.load(f)
                users = data.get("users", {}) or {}
                for u in users.values():
                    cur.execute(
                        """
                        INSERT OR IGNORE INTO users (
                            id, username, password_hash, created_at,
                            mouse_x, mouse_y, is_online, difficulty
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            u.get("id"),
                            u.get("username"),
                            u.get("password"),
                            u.get("created_at", ""),
                            float(u.get("mouse_x", 0.0)),
                            float(u.get("mouse_y", 0.0)),
                            1 if u.get("is_online") else 0,
                            float(u.get("difficulty", 1.0)),
                        ),
                    )
                conn.commit()

                # Remove users from JSON to avoid storing password hashes going forward
                data["users"] = {}
                with open(json_path, "w") as f:
                    json.dump(data, f, indent=2)
            except Exception:
                # Best-effort migration; if it fails, leave JSON as-is
                pass
    finally:
        conn.close()