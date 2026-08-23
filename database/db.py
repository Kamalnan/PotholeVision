import sqlite3
from datetime import datetime
import math

DB_PATH = 'database/detections.db'

def init_db():
    """Creates the detections table if it doesn't already exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            latitude REAL,
            longitude REAL,
            confidence REAL,
            image_path TEXT,
            times_detected INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def haversine_distance(lat1, lon1, lat2, lon2):
    """Returns distance in meters between two GPS coordinates."""
    R = 6371000  # Earth's radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def log_detection(latitude, longitude, confidence, image_path, proximity_threshold=10):
    """
    Logs a detection. If GPS is available and a nearby detection (within
    proximity_threshold meters) already exists, increments its count instead
    of creating a duplicate entry.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if latitude is not None and longitude is not None:
        cursor.execute('SELECT id, latitude, longitude FROM detections WHERE latitude IS NOT NULL')
        for row in cursor.fetchall():
            existing_id, existing_lat, existing_lon = row
            dist = haversine_distance(latitude, longitude, existing_lat, existing_lon)
            if dist <= proximity_threshold:
                cursor.execute(
                    'UPDATE detections SET times_detected = times_detected + 1, timestamp = ? WHERE id = ?',
                    (datetime.now().isoformat(), existing_id)
                )
                conn.commit()
                conn.close()
                return existing_id  # updated existing entry, not a new one

    # No nearby match found (or no GPS) — insert as new
    cursor.execute(
        'INSERT INTO detections (timestamp, latitude, longitude, confidence, image_path) VALUES (?, ?, ?, ?, ?)',
        (datetime.now().isoformat(), latitude, longitude, confidence, image_path)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id

def get_all_detections():
    """Returns all logged detections."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM detections')
    rows = cursor.fetchall()
    conn.close()
    return rows