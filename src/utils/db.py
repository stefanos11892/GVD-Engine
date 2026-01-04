"""
SQLite Database Layer for GVD Engine
=====================================
Provides thread-safe data persistence replacing CSV/JSON files.
Uses SQLAlchemy for connection pooling and ORM capabilities.
"""
import os
import sqlite3
import json
import logging
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
import threading

logger = logging.getLogger("Database")

# ======================================
# DATABASE PATH CONFIGURATION
# ======================================
def _get_db_path():
    """Returns the path to the SQLite database file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, 'gvd_engine.db')

DB_PATH = _get_db_path()

# Thread-local storage for connections
_local = threading.local()

# ======================================
# CONNECTION MANAGEMENT
# ======================================
def get_connection() -> sqlite3.Connection:
    """
    Returns a thread-local SQLite connection.
    Each thread gets its own connection for thread safety.
    """
    if not hasattr(_local, 'connection') or _local.connection is None:
        _local.connection = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.connection.row_factory = sqlite3.Row  # Enable dict-like access
        _local.connection.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for concurrency
        _local.connection.execute("PRAGMA foreign_keys=ON")
    return _local.connection

@contextmanager
def get_cursor():
    """Context manager for database cursor with automatic commit/rollback."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        cursor.close()

# ======================================
# SCHEMA INITIALIZATION
# ======================================
def init_database():
    """Creates tables if they don't exist."""
    with get_cursor() as cursor:
        # Holdings table (replaces master_portfolio.csv)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                isin TEXT,
                currency TEXT DEFAULT 'USD',
                shares REAL DEFAULT 0,
                opening_price REAL DEFAULT 0,
                current_price REAL DEFAULT 0,
                unrealised_pl REAL DEFAULT 0,
                value_source REAL DEFAULT 0,
                fx_rate REAL DEFAULT 1,
                unrealised_pl_base REAL DEFAULT 0,
                market_value REAL DEFAULT 0,
                allocation_pct REAL DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker)
            )
        """)
        
        # Account info table (replaces account_info.json)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_info (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transactions table (replaces transactions.csv)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                type TEXT,
                ticker TEXT,
                shares REAL,
                price REAL,
                amount REAL,
                currency TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Verification logs table (for audit trail)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                timestamp TEXT,
                pdf_path TEXT,
                report_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
    logger.info("Database schema initialized.")

# ======================================
# HOLDINGS CRUD OPERATIONS
# ======================================
def upsert_holding(holding: Dict[str, Any]) -> None:
    """Insert or update a holding by ticker."""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO holdings (ticker, isin, currency, shares, opening_price, current_price,
                                  unrealised_pl, value_source, fx_rate, unrealised_pl_base,
                                  market_value, allocation_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker) DO UPDATE SET
                isin = excluded.isin,
                currency = excluded.currency,
                shares = excluded.shares,
                opening_price = excluded.opening_price,
                current_price = excluded.current_price,
                unrealised_pl = excluded.unrealised_pl,
                value_source = excluded.value_source,
                fx_rate = excluded.fx_rate,
                unrealised_pl_base = excluded.unrealised_pl_base,
                market_value = excluded.market_value,
                allocation_pct = excluded.allocation_pct,
                updated_at = CURRENT_TIMESTAMP
        """, (
            holding.get('Ticker', holding.get('ticker', '')),
            holding.get('ISIN', holding.get('isin', '')),
            holding.get('Currency', holding.get('currency', 'USD')),
            holding.get('Shares', holding.get('shares', 0)),
            holding.get('Opening Price', holding.get('opening_price', 0)),
            holding.get('Current Price', holding.get('current_price', 0)),
            holding.get('Unrealised P/L', holding.get('unrealised_pl', 0)),
            holding.get('Value (Source)', holding.get('value_source', 0)),
            holding.get('FX Rate', holding.get('fx_rate', 1)),
            holding.get('Unrealised P/L (Base)', holding.get('unrealised_pl_base', 0)),
            holding.get('Market Value', holding.get('market_value', 0)),
            holding.get('Allocation %', holding.get('allocation_pct', 0))
        ))

def get_all_holdings() -> List[Dict[str, Any]]:
    """Returns all holdings as a list of dicts."""
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM holdings ORDER BY market_value DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

def clear_holdings() -> None:
    """Removes all holdings (for full refresh)."""
    with get_cursor() as cursor:
        cursor.execute("DELETE FROM holdings")

# ======================================
# ACCOUNT INFO CRUD OPERATIONS
# ======================================
def set_account_value(key: str, value: Any) -> None:
    """Sets an account info key-value pair."""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO account_info (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
        """, (key, json.dumps(value)))

def get_account_value(key: str, default: Any = None) -> Any:
    """Gets an account info value by key."""
    with get_cursor() as cursor:
        cursor.execute("SELECT value FROM account_info WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            return json.loads(row['value'])
        return default

def get_all_account_info() -> Dict[str, Any]:
    """Returns all account info as a dict."""
    with get_cursor() as cursor:
        cursor.execute("SELECT key, value FROM account_info")
        rows = cursor.fetchall()
        return {row['key']: json.loads(row['value']) for row in rows}

# ======================================
# TRANSACTIONS CRUD OPERATIONS
# ======================================
def insert_transaction(transaction: Dict[str, Any]) -> None:
    """Inserts a new transaction."""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT INTO transactions (date, type, ticker, shares, price, amount, currency, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction.get('date', ''),
            transaction.get('type', ''),
            transaction.get('ticker', ''),
            transaction.get('shares', 0),
            transaction.get('price', 0),
            transaction.get('amount', 0),
            transaction.get('currency', 'USD'),
            transaction.get('notes', '')
        ))

def get_all_transactions() -> List[Dict[str, Any]]:
    """Returns all transactions."""
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

# Initialize database on module load
init_database()
