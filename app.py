from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness_v3.db"

# Core factors from Aceestver-2.1.2.py
programs = {
    "Fat Loss (FL)": {"factor": 22},
    "Muscle Gain (MG)": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}

def init_db():
    """Initializes multi-table schema for clients and adherence tracking"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, age INTEGER, weight REAL, program TEXT, calories INTEGER
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "2.1.2"}), 200

@app.route('/api/client', methods=['POST'])
def save_client():
    data = request.json
    name, age, weight = data.get('name'), data.get('age'), data.get('weight')
    program = data.get('program')

    if not name or program not in programs:
        return jsonify({"error": "Name and valid Program required"}), 400

    calories = int(float(weight) * programs[program]["factor"])

    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO clients (name, age, weight, program, calories) VALUES (?,?,?,?,?)",
                    (name, age, weight, program, calories))
        conn.commit()
        return jsonify({"message": f"Client {name} saved", "calories": calories}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/progress', methods=['POST'])
def save_progress():
    """Logs weekly adherence metrics"""
    data = request.json
    name, adherence = data.get('name'), data.get('adherence', 0)
    week = datetime.now().strftime("Week %U - %Y")

    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
                    (name, week, adherence))
        conn.commit()
        return jsonify({"message": "Weekly progress logged", "week": week}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)