import sqlite3
import os
from pathlib import Path
from ..config import DEFAULTS

def init_db(db_path: str = None):
    db_path = db_path or DEFAULTS["DB_PATH"]
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    cur.executescript(sql)
    # lightweight migrations for existing DBs: add new audit columns if missing
    try:
        cur.execute("ALTER TABLE audit_log ADD COLUMN origem TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE audit_log ADD COLUMN before_payload TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE audit_log ADD COLUMN after_payload TEXT")
    except Exception:
        pass
    try:
        cur.execute("ALTER TABLE audit_log ADD COLUMN user_id INTEGER")
    except Exception:
        pass
    # ensure history tables exist (safe due to IF NOT EXISTS in schema)
    # commit migrations
    conn.commit()
    conn.close()
    return db_path

if __name__ == '__main__':
    print("Initializing DB at", init_db())
