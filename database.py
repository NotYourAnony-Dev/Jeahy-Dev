import sqlite3
import threading
from config import Config

_local = threading.local()

def get_conn() -> sqlite3.Connection:
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
        _local.conn.execute("PRAGMA journal_mode=WAL")
        _local.conn.execute("PRAGMA synchronous=NORMAL")
        _local.conn.execute("PRAGMA cache_size=2000")
        _local.conn.execute("PRAGMA temp_store=MEMORY")
    return _local.conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            username    TEXT,
            full_name   TEXT,
            joined_at   TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS chats (
            chat_id     INTEGER PRIMARY KEY,
            title       TEXT,
            chat_type   TEXT,
            joined_at   TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS warns (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            reason      TEXT,
            warned_at   TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS locks (
            chat_id     INTEGER PRIMARY KEY,
            lock_links  INTEGER DEFAULT 0,
            lock_spam   INTEGER DEFAULT 0,
            lock_all    INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS settings (
            chat_id     INTEGER PRIMARY KEY,
            welcome_on  INTEGER DEFAULT 1,
            welcome_msg TEXT DEFAULT '',
            lang        TEXT DEFAULT 'en'
        );
        CREATE TABLE IF NOT EXISTS flood (
            chat_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            count       INTEGER DEFAULT 0,
            last_msg    REAL DEFAULT 0,
            PRIMARY KEY (chat_id, user_id)
        );
        CREATE TABLE IF NOT EXISTS raid (
            chat_id     INTEGER PRIMARY KEY,
            count       INTEGER DEFAULT 0,
            last_join   REAL DEFAULT 0,
            active      INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS game_data (
            chat_id     INTEGER PRIMARY KEY,
            last_word   TEXT DEFAULT '',
            started_by  INTEGER DEFAULT 0
        );
    """)
    conn.commit()

# ── User helpers ──────────────────────────────────────────────────────────────
def upsert_user(user_id: int, username: str, full_name: str):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO users (user_id, username, full_name) VALUES (?,?,?)",
        (user_id, username or "", full_name or "")
    )
    conn.commit()

def get_user(user_id: int):
    return get_conn().execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()

# ── Chat helpers ──────────────────────────────────────────────────────────────
def upsert_chat(chat_id: int, title: str, chat_type: str):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO chats (chat_id, title, chat_type) VALUES (?,?,?)",
        (chat_id, title or "", chat_type or "")
    )
    conn.commit()

# ── Warn helpers ──────────────────────────────────────────────────────────────
def add_warn(chat_id: int, user_id: int, reason: str = "") -> int:
    conn = get_conn()
    conn.execute("INSERT INTO warns (chat_id, user_id, reason) VALUES (?,?,?)",
                 (chat_id, user_id, reason))
    conn.commit()
    row = conn.execute("SELECT COUNT(*) FROM warns WHERE chat_id=? AND user_id=?",
                       (chat_id, user_id)).fetchone()
    return row[0]

def get_warns(chat_id: int, user_id: int) -> int:
    row = get_conn().execute(
        "SELECT COUNT(*) FROM warns WHERE chat_id=? AND user_id=?",
        (chat_id, user_id)
    ).fetchone()
    return row[0]

def reset_warns(chat_id: int, user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM warns WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    conn.commit()

# ── Lock helpers ──────────────────────────────────────────────────────────────
def get_locks(chat_id: int) -> dict:
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO locks (chat_id) VALUES (?)", (chat_id,)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM locks WHERE chat_id=?", (chat_id,)).fetchone()
    return dict(row)

def set_lock(chat_id: int, lock_type: str, value: int):
    allowed = {"lock_links", "lock_spam", "lock_all"}
    if lock_type not in allowed:
        return
    conn = get_conn()
    conn.execute(f"INSERT OR IGNORE INTO locks (chat_id) VALUES (?)", (chat_id,))
    conn.execute(f"UPDATE locks SET {lock_type}=? WHERE chat_id=?", (value, chat_id))
    conn.commit()

# ── Flood helpers ─────────────────────────────────────────────────────────────
def get_flood(chat_id: int, user_id: int):
    row = get_conn().execute(
        "SELECT count, last_msg FROM flood WHERE chat_id=? AND user_id=?",
        (chat_id, user_id)
    ).fetchone()
    return (row["count"], row["last_msg"]) if row else (0, 0.0)

def set_flood(chat_id: int, user_id: int, count: int, last_msg: float):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO flood (chat_id, user_id, count, last_msg) VALUES (?,?,?,?)",
        (chat_id, user_id, count, last_msg)
    )
    conn.commit()

def reset_flood(chat_id: int, user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM flood WHERE chat_id=? AND user_id=?", (chat_id, user_id))
    conn.commit()

# ── Raid helpers ──────────────────────────────────────────────────────────────
def get_raid(chat_id: int):
    row = get_conn().execute(
        "SELECT count, last_join, active FROM raid WHERE chat_id=?", (chat_id,)
    ).fetchone()
    return (row["count"], row["last_join"], bool(row["active"])) if row else (0, 0.0, False)

def set_raid(chat_id: int, count: int, last_join: float, active: int):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO raid (chat_id, count, last_join, active) VALUES (?,?,?,?)",
        (chat_id, count, last_join, active)
    )
    conn.commit()

# ── Game helpers ──────────────────────────────────────────────────────────────
def get_game(chat_id: int):
    row = get_conn().execute(
        "SELECT last_word, started_by FROM game_data WHERE chat_id=?", (chat_id,)
    ).fetchone()
    return (row["last_word"], row["started_by"]) if row else ("", 0)

def set_game(chat_id: int, last_word: str, started_by: int):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO game_data (chat_id, last_word, started_by) VALUES (?,?,?)",
        (chat_id, last_word, started_by)
    )
    conn.commit()

def reset_game(chat_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM game_data WHERE chat_id=?", (chat_id,))
    conn.commit()

# ── Stats helpers ─────────────────────────────────────────────────────────────
def total_users() -> int:
    return get_conn().execute("SELECT COUNT(*) FROM users").fetchone()[0]

def total_chats() -> int:
    return get_conn().execute("SELECT COUNT(*) FROM chats").fetchone()[0]
