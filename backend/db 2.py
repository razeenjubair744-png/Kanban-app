import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional

from .schemas import BoardData

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "app.db"
DEFAULT_USER = {"username": "user", "password": "password", "token": "user-token"}
DEFAULT_BOARD: Dict[str, Any] = {
    "columns": [
        {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-2"]},
        {"id": "col-discovery", "title": "Discovery", "cardIds": ["card-3"]},
        {"id": "col-progress", "title": "In Progress", "cardIds": ["card-4", "card-5"]},
        {"id": "col-review", "title": "Review", "cardIds": ["card-6"]},
        {"id": "col-done", "title": "Done", "cardIds": ["card-7", "card-8"]},
    ],
    "cards": {
        "card-1": {
            "id": "card-1",
            "title": "Align roadmap themes",
            "details": "Draft quarterly themes with impact statements and metrics.",
        },
        "card-2": {
            "id": "card-2",
            "title": "Gather customer signals",
            "details": "Review support tags, sales notes, and churn feedback.",
        },
        "card-3": {
            "id": "card-3",
            "title": "Prototype analytics view",
            "details": "Sketch initial dashboard layout and key drill-downs.",
        },
        "card-4": {
            "id": "card-4",
            "title": "Refine status language",
            "details": "Standardize column labels and tone across the board.",
        },
        "card-5": {
            "id": "card-5",
            "title": "Design card layout",
            "details": "Add hierarchy and spacing for scanning dense lists.",
        },
        "card-6": {
            "id": "card-6",
            "title": "QA micro-interactions",
            "details": "Verify hover, focus, and loading states.",
        },
        "card-7": {
            "id": "card-7",
            "title": "Ship marketing page",
            "details": "Final copy approved and asset pack delivered.",
        },
        "card-8": {
            "id": "card-8",
            "title": "Close onboarding sprint",
            "details": "Document release notes and share internally.",
        },
    },
}


def get_db_path() -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(str(get_db_path()), check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    conn = get_connection()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                token TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS boards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                board_json TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """
        )
        conn.commit()
        if not get_user_by_username(conn, DEFAULT_USER["username"]):
            create_user(conn, DEFAULT_USER["username"], DEFAULT_USER["password"], DEFAULT_USER["token"])
        if not get_board_for_username(conn, DEFAULT_USER["username"]):
            save_board_for_username(conn, DEFAULT_USER["username"], BoardData.model_validate(DEFAULT_BOARD))
    finally:
        conn.close()


def create_user(conn: sqlite3.Connection, username: str, password: str, token: str) -> None:
    conn.execute(
        "INSERT OR IGNORE INTO users (username, password, token) VALUES (?, ?, ?)",
        (username, password, token),
    )
    conn.commit()


def get_user_by_username(conn: sqlite3.Connection, username: str) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT id, username, password, token FROM users WHERE username = ?", (username,)).fetchone()
    return dict(row) if row else None


def get_user_by_token(conn: sqlite3.Connection, token: str) -> Optional[Dict[str, Any]]:
    row = conn.execute("SELECT id, username, password, token FROM users WHERE token = ?", (token,)).fetchone()
    return dict(row) if row else None


def get_board_for_username(conn: sqlite3.Connection, username: str) -> Optional[BoardData]:
    user = get_user_by_username(conn, username)
    if not user:
        return None

    row = conn.execute(
        "SELECT board_json FROM boards WHERE user_id = ?",
        (user["id"],),
    ).fetchone()
    if not row:
        return None

    board = json.loads(row["board_json"])
    return BoardData.model_validate(board)


def save_board_for_username(conn: sqlite3.Connection, username: str, board: BoardData) -> None:
    user = get_user_by_username(conn, username)
    if not user:
        raise ValueError("User does not exist")

    board_json = json.dumps(board.model_dump())
    existing = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user["id"],)).fetchone()
    if existing:
        conn.execute(
            "UPDATE boards SET board_json = ? WHERE user_id = ?",
            (board_json, user["id"]),
        )
    else:
        conn.execute(
            "INSERT INTO boards (user_id, board_json) VALUES (?, ?)",
            (user["id"], board_json),
        )
    conn.commit()
