from flask import Flask, request, jsonify, send_file, render_template_string
import sqlite3
from datetime import datetime, date
import secrets
import os
from fpdf import FPDF

app = Flask(__name__)
DB_NAME = "aceest_fitness_v8.db"

# Core factors updated for v3.2.4
programs = {
    "Fat Loss": {"factor": 22},
    "Muscle Gain": {"factor": 35},
    "Beginner": {"factor": 26}
}

program_templates = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"]
}

def init_db():
    """Initializes schema including membership tracking for v3.2.4"""
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT)")
    cur.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin','admin','Admin')")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, 
        weight REAL, program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER, 
        membership_status TEXT, membership_end TEXT)""")
        
    cur.execute("CREATE TABLE IF NOT EXISTS progress (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS metrics (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL)")
    cur.execute("CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS exercises (id INTEGER PRIMARY KEY AUTOINCREMENT, workout_id INTEGER, name TEXT, sets INTEGER, reps INTEGER, weight REAL)")
    conn.commit(); conn.close()

init_db()

@app.route('/')
def home():
    """Main Dashboard for Kubernetes Visibility using your existing SQLite setup"""
    try:
        conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        user_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM clients")
        client_count = cur.fetchone()[0]
        conn.close()
        
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ACEest Platform - Dashboard</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 40px; }
                .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
                h1 { color: #1a73e8; border-bottom: 2px solid #e8f0fe; padding-bottom: 10px; }
                .status-bar { background: #e6f4ea; color: #1e8e3e; padding: 10px; border-radius: 6px; font-weight: bold; margin-bottom: 20px; }
                .stats-grid { display: flex; gap: 20px; margin: 20px 0; }
                .stat-card { flex: 1; background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #dee2e6; }
                .stat-number { font-size: 24px; font-weight: bold; color: #202124; }
                .stat-label { color: #5f6368; font-size: 14px; text-transform: uppercase; }
                .links { margin-top: 30px; font-size: 14px; }
                a { color: #1a73e8; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>ACEest Fitness & Performance</h1>
                <div class="status-bar">● System Operational (K8s Cluster: Minikube)</div>
                <p>Welcome to the Platform Dashboard. The application is processing requests on port 5000.</p>
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{{ user_count }}</div>
                        <div class="stat-label">Registered Admins</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{{ client_count }}</div>
                        <div class="stat-label">Total Clients</div>
                    </div>
                </div>
                <div class="links">
                    <strong>Quick Links:</strong> 
                    | <a href="/health">API Health Check</a> 
                </div>
                <p style="color: #9aa0a6; font-size: 12px; margin-top: 40px;">Version: 3.2.4 | Deployment: RollingUpdate</p>
            </div>
        </body>
        </html>
        """, user_count=user_count, client_count=client_count)
    except Exception as e:
        return f"Database Connection Error: {str(e)}", 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "3.2.4"}), 200

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=? AND password=?", (data.get('username'), data.get('password')))
    row = cur.fetchone(); conn.close()
    if row: return jsonify({"message": "Login successful", "role": row[0]}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/client', methods=['POST'])
def save_client():
    data = request.json
    name, weight, program = data.get('name'), data.get('weight'), data.get('program')
    if not name or program not in programs: return jsonify({"error": "Invalid input"}), 400
    calories = int(float(weight) * programs[program]["factor"])
    
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("""INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories, membership_status, membership_end) 
        VALUES (?,?,?,?,?,?,?,?)""",
        (name, data.get('age'), data.get('height'), weight, program, calories, data.get('membership_status', 'Active'), data.get('membership_end')))
    conn.commit(); conn.close()
    return jsonify({"message": f"Client saved", "calories": calories}), 201

@app.route('/api/membership/<name>', methods=['GET'])
def check_membership(name):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT membership_status, membership_end FROM clients WHERE name=?", (name,))
    row = cur.fetchone(); conn.close()
    if not row: return jsonify({"error": "Client not found"}), 404
    return jsonify({"name": name, "status": row[0], "end_date": row[1]}), 200

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

@app.route('/api/workout', methods=['POST'])
def log_workout():
    data = request.json
    name, w_type = data.get('name'), data.get('type')
    if not name or not w_type: return jsonify({"error": "Name and workout type are required"}), 400

    w_date = data.get('date', date.today().isoformat())
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)",
                (name, w_date, w_type, data.get('duration', 60), data.get('notes', '')))
    workout_id = cur.lastrowid
    conn.commit(); conn.close()
    return jsonify({"message": "Workout saved", "workout_id": workout_id}), 201

@app.route('/api/workouts/<name>', methods=['GET'])
def get_workouts(name):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT date, workout_type, duration_min, notes FROM workouts WHERE client_name=? ORDER BY date DESC", (name,))
    rows = cur.fetchall(); conn.close()
    return jsonify([{"date": r[0], "type": r[1], "duration": r[2], "notes": r[3]} for r in rows]), 200

@app.route('/api/program/generate', methods=['POST'])
def generate_program():
    data = request.json
    name, focus = data.get('name'), data.get('focus', 'Beginner')
    if focus not in program_templates: return jsonify({"error": "Invalid focus area"}), 400

    program_detail = secrets.choice(program_templates[focus])
    
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("UPDATE clients SET program=? WHERE name=?", (program_detail, name))
    conn.commit(); conn.close()
    
    return jsonify({"message": "Program Generated", "program": program_detail}), 200

@app.route('/api/report/<name>', methods=['GET'])
def get_report(name):
    conn = sqlite3.connect(DB_NAME); cur = conn.cursor()
    cur.execute("SELECT * FROM clients WHERE name=?", (name,))
    row = cur.fetchone(); conn.close()
    if not row: return jsonify({"error": "Client not found"}), 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"ACEest Client Report - {name}", ln=True, align="L")
    pdf.set_font("Arial", "", 12); pdf.ln(10)
    pdf.cell(0, 10, f"Age: {row[2]}", ln=True)
    pdf.cell(0, 10, f"Weight: {row[4]} kg", ln=True)
    pdf.cell(0, 10, f"Program: {row[5]}", ln=True)
    pdf.cell(0, 10, f"Membership: {row[9]}", ln=True)
    pdf.cell(0, 10, f"End Date: {row[10]}", ln=True)
    
    filepath = f"{name}_report.pdf"
    pdf.output(filepath)
    return send_file(filepath, as_attachment=True)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)