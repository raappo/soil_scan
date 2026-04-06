import sqlite3
from datetime import datetime

DB_NAME = "soil_scan.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            filename TEXT,
            particle_count INTEGER,
            fiber_count INTEGER,
            fragment_count INTEGER,
            soil_weight REAL,
            concentration REAL,
            risk_level TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_scan(filename, count, fibers, fragments, weight, concentration, risk, lat=None, lon=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO scans (timestamp, filename, particle_count, fiber_count, fragment_count, 
                           soil_weight, concentration, risk_level, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, filename, count, fibers, fragments, weight, concentration, risk, lat, lon))
    conn.commit()
    conn.close()

def get_all_scans():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM scans ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows