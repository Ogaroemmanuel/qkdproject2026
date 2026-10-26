import sqlite3
import bcrypt
from datetime import datetime
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
            kill_switch BOOLEAN
        )
    ''')
    
    # 2. Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
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
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        stored_hash = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True
    return False

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
def log_simulation(key_size, num_shots, eve_active, qber, threshold, status, kill_switch):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO simulation_runs 
        (timestamp, key_size, num_shots, eve_active, qber_value, threshold_used, status, kill_switch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, key_size, num_shots, eve_active, qber, threshold, status, kill_switch))
    conn.commit()
    conn.close()

def fetch_logs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM simulation_runs ORDER BY run_id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows
