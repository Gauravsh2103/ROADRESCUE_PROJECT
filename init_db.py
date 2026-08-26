import sqlite3
from werkzeug.security import generate_password_hash

def init_db():
    conn = sqlite3.connect('roadrescue.db')
    cursor = conn.cursor()

    # 1. Commuter Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 2. Mechanics Table (With Status and Live Coordinates)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mechanics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            specialization TEXT NOT NULL,
            latitude REAL DEFAULT 21.2589,  -- Default to CSVTU
            longitude REAL DEFAULT 81.3534, -- Default to CSVTU
            is_active INTEGER DEFAULT 0,     -- 0 = Offline, 1 = Online
            base_charge INTEGER DEFAULT 150, -- Base visit charge in Rs.
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Kuch pre-populated mechanics insert kar dete hain default password 'bhilai123' ke sath check karne ke liye
    cursor.execute("SELECT COUNT(*) FROM mechanics")
    if cursor.fetchone()[0] == 0:
        default_hash = generate_password_hash("bhilai123")
        mechanics_data = [
            ("Sharma Garage", "sharma@rescue.com", "9876543210", default_hash, "Tyre Repair", 21.2489, 81.3434, 1, 150),
            ("Bhilai Battery House", "battery@rescue.com", "8877665544", default_hash, "Battery & Electric", 21.2689, 81.3634, 1, 200),
            ("Sahu Motor Repair", "sahu@rescue.com", "7766554433", default_hash, "Engine & Brake", 21.2520, 81.3550, 1, 250),
            ("Quick Mechanics", "quick@rescue.com", "9988776655", default_hash, "All-rounder", 21.2589, 81.3534, 1, 100)
        ]
        cursor.executemany('''
            INSERT INTO mechanics (name, email, phone, password_hash, specialization, latitude, longitude, is_active, base_charge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', mechanics_data)
        print("💡 Dummy verified mechanics pre-loaded successfully!")

    conn.commit()
    conn.close()
    print("🚀 Database upgraded successfully with dual-role security schemas!")

if __name__ == '__main__':
    init_db()