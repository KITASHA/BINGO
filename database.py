import sqlite3
from pathlib import Path


DB_DIR = Path("data")
DB_PATH = DB_DIR / "bingo.db"


def get_connection():
    DB_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn