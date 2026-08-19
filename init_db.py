import sqlite3

def init_db():
    conn = sqlite3.connect('roadrescue.db')
    cursor = conn.cursor()
    
    # 1. Create mechanics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mechanics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            specialties TEXT NOT NULL,
            rating REAL NOT NULL,
            base_cost INTEGER NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    ''')
    
    # 2. Mock data near CSVTU New Campus, Bhilai (Lat: 21.2064, Long: 81.2552)
    # This makes the distances incredibly realistic during your project demo!
    mechanics = [
        ("CSVTU Auto Experts (Outside Gate)", "+919876543214", "Flat Tyre, Dead Battery, Engine Smoke, Engine Overheat, Brake Failure, Towing Needed, Out of Fuel, Key Lockout", 4.9, 150, 21.2055, 81.2535), # ~0.2 km away
        ("Speedy Motors (Junwani)", "+919876543210", "Flat Tyre, Dead Battery, Key Lockout, Out of Fuel", 4.8, 120, 21.2132, 81.2592), # ~1.1 km away
        ("Sai Baba Garage (Nehru Nagar)", "+919876543211", "Engine Smoke, Engine Overheat, Brake Failure, Towing Needed", 4.6, 300, 21.2185, 81.3032), # ~5.3 km away
        ("Durg Roadside Care Center", "+919876543212", "Flat Tyre, Out of Fuel, Key Lockout", 4.3, 100, 21.1904, 81.2828), # ~3.5 km away
        ("Apex Towing Services (Supela)", "+919876543213", "Towing Needed, Brake Failure", 4.7, 800, 21.2139, 81.3283) # ~7.5 km away
    ]
    
    # Clear old data to prevent duplication during testing
    cursor.execute('DELETE FROM mechanics')
    
    # 3. Insert mock mechanics
    cursor.executemany('''
        INSERT INTO mechanics (name, phone, specialties, rating, base_cost, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', mechanics)
    
    conn.commit()
    conn.close()
    print("🎉 Database 'roadrescue.db' successfully initialized with CSVTU/Bhilai local mechanics!")

if __name__ == '__main__':
    init_db()