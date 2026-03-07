from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime, date

app = Flask(__name__)
DB_NAME = "aceest_fitness_v6.db"

# Core factors
programs = {
    "Fat Loss (FL) – 3 day": {"factor": 22},
    "Fat Loss (FL) – 5 day": {"factor": 24},
    "Muscle Gain (MG) – PPL": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}

def init_db():
    """Initializes the complete v3.0.1 relational schema"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, weight REAL, program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, workout_id INTEGER, name TEXT, sets INTEGER, reps INTEGER, weight REAL)""")
    conn.commit()
    conn.close()

init_db()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "3.0.1"}), 200

@app.route('/api/client', methods=['POST'])
def save_client():
    data = request.json
    name, weight, program = data.get('name'), data.get('weight'), data.get('program')
    if not name or program not in programs:
        return jsonify({"error": "Invalid client data or program"}), 400
    calories = int(float(weight) * programs[program]["factor"])
    
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("""INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence) VALUES (?,?,?,?,?,?,?,?)""",
        (name, data.get('age'), data.get('height'), weight, program, calories, data.get('target_weight'), data.get('target_adherence')))
    conn.commit(); conn.close()
    return jsonify({"message": f"Client {name} saved", "calories": calories}), 201

@app.route('/api/progress', methods=['POST'])
def save_progress():
    data = request.json
    week = datetime.now().strftime("Week %U - %Y")
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)", (data.get('name'), week, data.get('adherence', 0)))
    conn.commit(); conn.close()
    return jsonify({"message": "Progress logged", "week": week}), 201

@app.route('/api/progress/<name>', methods=['GET'])
def get_progress(name):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (name,))
    rows = cur.fetchall(); conn.close()
    return jsonify([{"week": r[0], "adherence": r[1]} for r in rows]), 200

@app.route('/api/metrics', methods=['POST'])
def log_metrics():
    data = request.json
    m_date = data.get('date', date.today().isoformat())
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("INSERT INTO metrics (client_name, date, weight, waist, bodyfat) VALUES (?,?,?,?,?)",
                (data.get('name'), m_date, data.get('weight'), data.get('waist'), data.get('bodyfat')))
    conn.commit(); conn.close()
    return jsonify({"message": "Metrics logged"}), 201

@app.route('/api/bmi/<name>', methods=['GET'])
def get_bmi(name):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT height, weight FROM clients WHERE name=?", (name,))
    row = cur.fetchone(); conn.close()
    if not row or not row[0]: return jsonify({"error": "Data missing"}), 404
    bmi = round(row[1] / ((row[0]/100)**2), 1)
    return jsonify({"name": name, "bmi": bmi, "category": "Normal" if bmi < 25 else "Overweight"}), 200

# --- NEW v3.0.1 ENDPOINTS ---
@app.route('/api/workout', methods=['POST'])
def log_workout():
    """Logs a session-level workout and an optional associated exercise"""
    data = request.json
    name, w_type = data.get('name'), data.get('type')
    if not name or not w_type:
        return jsonify({"error": "Name and workout type are required"}), 400

    w_date = data.get('date', date.today().isoformat())
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    
    # Insert Workout
    cur.execute("INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)",
                (name, w_date, w_type, data.get('duration', 60), data.get('notes', '')))
    workout_id = cur.lastrowid
    
    # Insert Exercise if provided
    ex_name = data.get('ex_name')
    if ex_name:
        cur.execute("INSERT INTO exercises (workout_id, name, sets, reps, weight) VALUES (?, ?, ?, ?, ?)",
                    (workout_id, ex_name, data.get('ex_sets', 3), data.get('ex_reps', 10), data.get('ex_weight', 0.0)))
                    
    conn.commit(); conn.close()
    return jsonify({"message": "Workout saved", "workout_id": workout_id}), 201

@app.route('/api/workouts/<name>', methods=['GET'])
def get_workouts(name):
    """Retrieves workout history sorted by date for the Treeview GUI"""
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT date, workout_type, duration_min, notes FROM workouts WHERE client_name=? ORDER BY date DESC, id DESC", (name,))
    rows = cur.fetchall(); conn.close()
    return jsonify([{"date": r[0], "type": r[1], "duration": r[2], "notes": r[3]} for r in rows]), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)