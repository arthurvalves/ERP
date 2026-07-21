import sqlite3
from typing import Any, List, Tuple, Generator, Optional
from contextlib import contextmanager
from ..config import DEFAULTS
import os

DB_PATH = os.environ.get('DB_PATH', 'erp.db')

def get_connection(db_path: str = None):
    db_path = db_path or DEFAULTS.get("DB_PATH", "erp.db")
    conn = sqlite3.connect(db_path, timeout=15.0)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON;')
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA synchronous=NORMAL;')
    return conn

def fetchone(query: str, params: Tuple = ()): 
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    row = cur.fetchone()
    conn.close()
    return row

def fetchall(query: str, params: Tuple = ()): 
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def execute(query: str, params: Tuple = ()): 
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    lastrowid = cur.lastrowid
    conn.close()
    return lastrowid

def execute_with_conn(conn, query: str, params: Tuple = ()): 
    cur = conn.cursor()
    cur.execute(query, params)
    return cur.lastrowid

@contextmanager
def transaction(db_path: str = None) -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

