from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
DB_NAME = "aceest_fitness_v5.db"

# Core factors from the v2.2.4 baseline
programs = {
    "Fat Loss (FL) – 3 day": {"factor": 22},
    "Fat Loss (FL) – 5 day": {"factor": 24},
    "Muscle Gain (MG) – PPL": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}

def init_db():
    """Initializes the advanced relational schema for v2.2.4"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    # Relational Tables
    cur.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, 
        height REAL, weight REAL, program TEXT, calories INTEGER, 
        target_weight REAL, target_adherence INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, 
        week TEXT, adherence INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, 
        date TEXT, weight REAL, waist REAL, bodyfat REAL)""")
    conn.commit()
    conn.close()

init_db()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "2.2.4"}), 200

@app.route('/api/client', methods=['POST'])
def save_client():
    data = request.json
    name, weight, program = data.get('name'), data.get('weight'), data.get('program')
    
    if not name or program not in programs:
        return jsonify({"error": "Invalid client data or program"}), 400

    calories = int(float(weight) * programs[program]["factor"])
    
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("""INSERT OR REPLACE INTO clients 
        (name, age, height, weight, program, calories, target_weight, target_adherence) 
        VALUES (?,?,?,?,?,?,?,?)""",
        (name, data.get('age'), data.get('height'), weight, program, 
         calories, data.get('target_weight'), data.get('target_adherence')))
    conn.commit(); conn.close()
    return jsonify({"message": f"Client {name} saved", "calories": calories}), 201

@app.route('/api/progress', methods=['POST'])
def save_progress():
    data = request.json
    name, adherence = data.get('name'), data.get('adherence', 0)
    week = datetime.now().strftime("Week %U - %Y")
    
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)", 
                (name, week, adherence))
    conn.commit(); conn.close()
    return jsonify({"message": "Progress logged", "week": week}), 201

@app.route('/api/progress/<name>', methods=['GET'])
def get_progress(name):
    """Retrieves history for charts; Fixes NoneType error by ensuring a list return"""
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (name,))
    rows = cur.fetchall(); conn.close()
    # Explicitly return a list to prevent TypeError in tests
    return jsonify([{"week": r[0], "adherence": r[1]} for r in rows]), 200

@app.route('/api/metrics', methods=['POST'])
def log_metrics():
    """Logs body transformation metrics"""
    data = request.json
    name = data.get('name')
    m_date = data.get('date', date.today().isoformat())
    
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?,?,?,?,?)",
                (name, m_date, data.get('weight'), data.get('waist'), data.get('bodyfat')))
    conn.commit(); conn.close()
    return jsonify({"message": "Metrics logged"}), 201

@app.route('/api/bmi/<name>', methods=['GET'])
def get_bmi(name):
    """Calculates BMI and health category for the analytics tab"""
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT height, weight FROM clients WHERE name=?", (name,))
    row = cur.fetchone(); conn.close()
    
    if not row or not row[0]:
        return jsonify({"error": "Height and weight data missing"}), 404
        
    bmi = round(row[1] / ((row[0]/100)**2), 1)
    category = "Normal" if bmi < 25 else "Overweight" # Simplified for API
    
    return jsonify({"name": name, "bmi": bmi, "category": category}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)