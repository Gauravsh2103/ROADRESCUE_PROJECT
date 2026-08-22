import math
import sqlite3
from flask import Flask, render_template, jsonify, request, send_from_directory
import os

app = Flask(__name__)

# Haversine Formula for real physical distance calculation in km
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth's radius in km
    lat1_rad = math.radians(float(lat1))
    lon1_rad = math.radians(float(lon1))
    lat2_rad = math.radians(float(lat2))
    lon2_rad = math.radians(float(lon2))
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

# Dynamic cost factor based on vehicle load/complexity
def get_cost_multiplier(vehicle):
    if vehicle == 'Bike':
        return 1.0
    elif vehicle == 'Car':
        return 2.5
    elif vehicle == 'Truck':
        return 6.0
    return 1.0

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/location', methods=['POST'])
def get_nearby_mechanics():
    try:
        data = request.get_json()
        user_lat = data.get('latitude')
        user_long = data.get('longitude')
        vehicle = data.get('vehicle', 'Bike')
        issue = data.get('issue', 'Flat Tyre')
        
        if not user_lat or not user_long:
            return jsonify({"error": "GPS Latitude and longitude are required!"}), 400
            
        # Connect to SQLite Database
        conn = sqlite3.connect('roadrescue.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query all mechanics to filter based on specialties
        cursor.execute("SELECT * FROM mechanics")
        rows = cursor.fetchall()
        
        nearby_mechanics = []
        multiplier = get_cost_multiplier(vehicle)
        
        for row in rows:
            # Match user issue with comma-separated specialties in db
            specialties = [s.strip().lower() for s in row['specialties'].split(',')]
            if issue.lower() in specialties:
                dist = calculate_distance(user_lat, user_long, row['latitude'], row['longitude'])
                
                # Dynamic cost calculation
                calculated_cost = int(row['base_cost'] * multiplier)
                
                nearby_mechanics.append({
                    "id": row['id'],
                    "name": row['name'],
                    "phone": row['phone'],
                    "rating": row['rating'],
                    "distance": dist,
                    "cost": calculated_cost,
                    "latitude": row['latitude'],
                    "longitude": row['longitude']
                })
        
        conn.close()
        
        # Default sort: Nearest Distance (Fastest response)
        nearby_mechanics.sort(key=lambda x: x['distance'])
        
        return jsonify(nearby_mechanics)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
def serve_manifest():
    return app.send_static_file('manifest.json')

@app.route('/service-worker.js')
def serve_sw():
    return app.send_static_file('service-worker.js')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js', mimetype='application/javascript')