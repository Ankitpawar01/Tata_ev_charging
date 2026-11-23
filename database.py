"""
Tata Power EV Analytics — Unified Database Connector (PostgreSQL with SQLite Fallback)
Prioritizes PostgreSQL (psycopg2). If PostgreSQL is unavailable, gracefully falls back to SQLite.
"""
import os
import sqlite3

# Try importing dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try importing psycopg2
try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(BASE_DIR, "ev_analytics.db")

# PostgreSQL Config
PG_HOST = os.getenv("PGHOST", "localhost")
PG_PORT = os.getenv("PGPORT", "5432")
PG_USER = os.getenv("PGUSER", "postgres")
PG_PASSWORD = os.getenv("PGPASSWORD", "postgres")
PG_DATABASE = os.getenv("PGDATABASE", "tata_ev_db")

def test_postgres():
    """Test if PostgreSQL is reachable and tata_ev_db exists."""
    if not PSYCOPG2_AVAILABLE:
        return False, "psycopg2 library not installed"
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DATABASE,
            connect_timeout=2
        )
        conn.close()
        return True, "PostgreSQL Connected"
    except Exception as e:
        return False, str(e)

def get_db():
    """
    Returns (connection, db_type: 'postgres' | 'sqlite')
    """
    # 1. Try PostgreSQL first
    pg_ok, _ = test_postgres()
    if pg_ok:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            user=PG_USER,
            password=PG_PASSWORD,
            dbname=PG_DATABASE
        )
        return conn, "postgres"

    # 2. Fall back to SQLite
    if os.path.exists(SQLITE_DB_PATH):
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

    return None, "none"

def execute_query(query_sql, params=None):
    """
    Executes a SELECT query on the active database (Postgres or SQLite)
    and returns a list of dictionaries.
    Translates '?' parameter syntax to '%s' when running on PostgreSQL.
    """
    conn, db_type = get_db()
    if not conn:
        return [], db_type

    if params is None:
        params = []

    try:
        if db_type == "postgres":
            # Convert '?' placeholders to '%s' for psycopg2
            pg_query = query_sql.replace("?", "%s")
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(pg_query, params)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            # Convert RealDictRow to standard dict
            return [dict(r) for r in rows], db_type
        else: # sqlite
            cur = conn.cursor()
            cur.execute(query_sql, params)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return [dict(r) for r in rows], db_type
    except Exception as e:
        print(f"[!] Database Execution Error ({db_type}): {e}")
        try:
            conn.close()
        except Exception:
            pass
        return [], db_type

def execute_write(query_sql, params=None):
    """
    Executes an INSERT / UPDATE / DELETE query on the active database
    and commits. Returns (bool: success, str: message).
    """
    conn, db_type = get_db()
    if not conn:
        return False, "Database not available"

    if params is None:
        params = []

    try:
        if db_type == "postgres":
            pg_query = query_sql.replace("?", "%s")
            cur = conn.cursor()
            cur.execute(pg_query, params)
            conn.commit()
            cur.close()
            conn.close()
            return True, "Success"
        else:
            cur = conn.cursor()
            cur.execute(query_sql, params)
            conn.commit()
            cur.close()
            conn.close()
            return True, "Success"
    except Exception as e:
        print(f"[!] Database Write Error ({db_type}): {e}")
        try:
            conn.close()
        except Exception:
            pass
        return False, str(e)
