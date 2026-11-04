import sqlite3
import bcrypt
from datetime import datetime
import secrets
import time
import uuid
from pathlib import Path

DB_NAME = str(Path(__file__).resolve().parents[2] / "sd_qkd_results.db")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Simulation runs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS simulation_runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            key_size INTEGER,
            num_shots INTEGER,
            eve_active BOOLEAN,
            qber_value REAL,
            threshold_used REAL,
            status TEXT,
            kill_switch BOOLEAN,
            model_version TEXT NOT NULL DEFAULT 'legacy-before-bit-order-fix'
        )
    ''')
    
    # 2. Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            email_verified BOOLEAN NOT NULL DEFAULT 0
        )
    ''')

    run_columns = {row[1] for row in cursor.execute("PRAGMA table_info(simulation_runs)").fetchall()}
    if "model_version" not in run_columns:
        cursor.execute(
            "ALTER TABLE simulation_runs ADD COLUMN model_version TEXT NOT NULL DEFAULT 'legacy-before-bit-order-fix'"
        )

    # Existing local databases predate verified email. Additive migration keeps
    # those accounts usable while every new account is verified before insert.
    user_columns = {row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()}
    if "email" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "email_verified" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT 0")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users(email) WHERE email IS NOT NULL")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_registrations (
            email TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            password_hash BLOB NOT NULL,
            code_hash TEXT NOT NULL,
            expires_at REAL NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            issued_at REAL NOT NULL
        )
    ''')

    # 3. Active Sessions table (NEW: For 15-Minute Persistent Login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            last_active REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False 
    finally:
        conn.close()
    return success

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ? OR email = ?", (username, username.lower()))
    result = cursor.fetchone()
    conn.close()
    if result:
        stored_hash = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True
    return False


def issue_registration_code(email, username, password):
    """Create a short-lived, single-use email verification challenge."""
    email = email.strip().lower()
    username = username.strip()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE username = ? OR lower(email) = ?", (username, email))
    if cursor.fetchone():
        conn.close()
        raise ValueError("That username or email is already registered.")

    now = time.time()
    cursor.execute("SELECT issued_at FROM pending_registrations WHERE email = ?", (email,))
    previous = cursor.fetchone()
    if previous and now - previous[0] < 60:
        conn.close()
        raise ValueError("Please wait a minute before requesting another code.")

    code = f"{secrets.randbelow(1_000_000):06d}"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    code_hash = bcrypt.hashpw(code.encode("utf-8"), bcrypt.gensalt())
    cursor.execute(
        """INSERT INTO pending_registrations
           (email, username, password_hash, code_hash, expires_at, attempts, issued_at)
           VALUES (?, ?, ?, ?, ?, 0, ?)
           ON CONFLICT(email) DO UPDATE SET username=excluded.username,
             password_hash=excluded.password_hash, code_hash=excluded.code_hash,
             expires_at=excluded.expires_at, attempts=0, issued_at=excluded.issued_at""",
        (email, username, password_hash, code_hash, now + 600, now),
    )
    conn.commit()
    conn.close()
    return code


def confirm_registration(email, code):
    """Verify an email code and atomically create the account."""
    email = email.strip().lower()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, password_hash, code_hash, expires_at, attempts FROM pending_registrations WHERE email = ?",
        (email,),
    )
    pending = cursor.fetchone()
    if not pending:
        conn.close()
        return False, "No active verification request was found. Request a new code."
    username, password_hash, expected, expires_at, attempts = pending
    if time.time() > expires_at:
        cursor.execute("DELETE FROM pending_registrations WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return False, "That code expired. Request a new verification code."
    if attempts >= 5:
        conn.close()
        return False, "Too many incorrect attempts. Request a new verification code."

    try:
        matches = bcrypt.checkpw(code.strip().encode("utf-8"), expected)
    except (TypeError, ValueError):
        matches = False
    if not matches:
        cursor.execute("UPDATE pending_registrations SET attempts = attempts + 1 WHERE email = ?", (email,))
        conn.commit()
        conn.close()
        return False, f"The code is incorrect. {4 - attempts} attempt(s) remaining."

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, email_verified) VALUES (?, ?, ?, 1)",
            (username, password_hash, email),
        )
        cursor.execute("DELETE FROM pending_registrations WHERE email = ?", (email,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return False, "That username or email is already registered."
    conn.close()
    return True, "Email verified. Your account is ready; sign in to continue."

# --- NEW: SESSION TOKEN MANAGEMENT ---
def create_session(username):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    token = str(uuid.uuid4()) # Generates a secure random string
    current_time = time.time()
    cursor.execute("INSERT INTO sessions (token, username, last_active) VALUES (?, ?, ?)", (token, username, current_time))
    conn.commit()
    conn.close()
    return token

def verify_session(token, max_idle_minutes=15):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, last_active FROM sessions WHERE token = ?", (token,))
    row = cursor.fetchone()
    
    if row:
        username, last_active = row
        current_time = time.time()
        # Verify the user has not been idle longer than 15 minutes
        if (current_time - last_active) <= (max_idle_minutes * 60):
            # Session is valid: Update their last_active timestamp so the 15-minute clock restarts
            cursor.execute("UPDATE sessions SET last_active = ? WHERE token = ?", (current_time, token))
            conn.commit()
            conn.close()
            return username
        else:
            # Session expired: Delete it for security
            cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()
    
    conn.close()
    return None

def destroy_session(token):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
    conn.commit()
    conn.close()

# --- SIMULATION LOGGING ---
def log_simulation(key_size, num_shots, eve_active, qber, threshold, status, kill_switch,
                   model_version="superdense-bit-order-corrected-v2"):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO simulation_runs 
        (timestamp, key_size, num_shots, eve_active, qber_value, threshold_used, status, kill_switch, model_version)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, key_size, num_shots, eve_active, qber, threshold, status, kill_switch, model_version))
    conn.commit()
    conn.close()

def fetch_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM simulation_runs ORDER BY run_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
