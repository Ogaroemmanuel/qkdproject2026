import sqlite3
import bcrypt
from datetime import datetime

DB_NAME = "sd_qkd_results.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Simulation runs table for your telemetry data
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
    
    # 2. Users table to secure the dashboard
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 3. Bcrypt Password Hashing
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False # Username already exists
    finally:
        conn.close()
    return success

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    # 4. Password Verification
    if result:
        stored_hash = result[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True
    return False

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