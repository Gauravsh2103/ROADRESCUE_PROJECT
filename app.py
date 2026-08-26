import os
import sqlite3
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.urandom(24) # Session security ke liye key

DB_FILE = 'roadrescue.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 1. Gateway Route (Login / Sign Up page)
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('commuter_portal'))
    if 'mechanic_id' in session:
        return redirect(url_for('mechanic_portal'))
    return render_template('login.html')

# 2. Register Route (POST only)
@app.route('/register', methods=['POST'])
def register():
    role_type = request.form.get('role_type')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    hashed_pw = generate_password_hash(password)
    conn = get_db_connection()
    
    try:
        if role_type == 'user':
            conn.execute(
                'INSERT INTO users (name, email, phone, password_hash) VALUES (?, ?, ?, ?)',
                (name, email, phone, hashed_pw)
            )
            flash("Account created! Please Sign In.")
        elif role_type == 'mechanic':
            specialization = request.form.get('specialization')
            conn.execute(
                'INSERT INTO mechanics (name, email, phone, password_hash, specialization, is_active) VALUES (?, ?, ?, ?, ?, 0)',
                (name, email, phone, hashed_pw, specialization)
            )
            flash("Mechanic profile registered! Please Sign In.")
        conn.commit()
    except sqlite3.IntegrityError:
        flash("Email already registered! Try another one.")
    finally:
        conn.close()
        
    return redirect(url_for('index'))

# 3. Login Route (POST only)
@app.route('/login', methods=['POST'])
def login():
    role_type = request.form.get('role_type')
    email = request.form.get('email')
    password = request.form.get('password')
    
    conn = get_db_connection()
    if role_type == 'user':
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = 'user'
            return redirect(url_for('commuter_portal'))
    elif role_type == 'mechanic':
        mech = conn.execute('SELECT * FROM mechanics WHERE email = ?', (email,)).fetchone()
        conn.close()
        if mech and check_password_hash(mech['password_hash'], password):
            session['mechanic_id'] = mech['id']
            session['mechanic_name'] = mech['name']
            session['role'] = 'mechanic'
            return redirect(url_for('mechanic_portal'))
            
    flash("Invalid Email or Password! Please try again.")
    return redirect(url_for('index'))

# 4. Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('index'))

# 5. Commuter Map Portal
@app.route('/portal/commuter')
def commuter_portal():
    if 'user_id' not in session:
        flash("Please login to access the system.")
        return redirect(url_for('index'))
    return render_template('index.html', name=session.get('user_name'))

# 6. Mechanic Dashboard Portal
@app.route('/portal/mechanic')
def mechanic_portal():
    if 'mechanic_id' not in session:
        flash("Please login to access the dashboard.")
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    mech_data = conn.execute('SELECT * FROM mechanics WHERE id = ?', (session['mechanic_id'],)).fetchone()
    conn.close()
    return render_template('mechanic.html', mech=mech_data)

# 7. Toggle Mechanic Duty Status (Online / Offline)
@app.route('/mechanic/toggle_status', methods=['POST'])
def toggle_status():
    if 'mechanic_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    data = request.json
    status = 1 if data.get('is_active') else 0
    
    conn = get_db_connection()
    conn.execute('UPDATE mechanics SET is_active = ? WHERE id = ?', (status, session['mechanic_id']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "is_active": status})

# 8. Update Mechanic Current Location
@app.route('/mechanic/update_location', methods=['POST'])
def update_location():
    if 'mechanic_id' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401
    
    data = request.json
    lat = data.get('lat')
    lon = data.get('lon')
    
    conn = get_db_connection()
    conn.execute('UPDATE mechanics SET latitude = ?, longitude = ? WHERE id = ?', (lat, lon, session['mechanic_id']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "lat": lat, "lon": lon})

# 9. API for Active Mechanics (Filtered: is_active = 1 only!)
@app.route('/api/mechanics', methods=['GET'])
def api_mechanics():
    conn = get_db_connection()
    # Sirf unhi mechanics ko select karenge jo ONLINE (is_active = 1) hain!
    active_mechs = conn.execute('SELECT id, name, phone, latitude, longitude, specialization, base_charge FROM mechanics WHERE is_active = 1').fetchall()
    conn.close()
    
    mechs_list = []
    for m in active_mechs:
        mechs_list.append({
            "id": m["id"],
            "name": m["name"],
            "phone": m["phone"],
            "lat": m["latitude"],
            "lon": m["longitude"],
            "specialization": m["specialization"],
            "base_charge": m["base_charge"]
        })
    return jsonify(mechs_list)

# PWA Service Worker Serve Route
@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'sw.js', mimetype='application/javascript')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)