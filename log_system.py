import sqlite3
from datetime import datetime

def log_access(username, status):
    conn = sqlite3.connect("IgateDB.db")
    cursor = conn.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO user_log (username, access_time, status)
        VALUES (?, ?, ?)
    """, (username, now, status))

    conn.commit()
    conn.close()
