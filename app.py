from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "aceest_fitness_v2.db"

# Core factors from Aceestver1.1.2.py baseline
programs = {
    "Fat Loss (FL)": {"factor": 22},
    "Muscle Gain (MG)": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}

def init_db():
    """Initializes the SQLite database for client persistence"""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            weight REAL,
            program TEXT,
            calories INTEGER
        )
    """)
    conn.commit()
    conn.close()

# Ensure the database exists on application startup
init_db()

@app.route('/health', methods=['GET'])
def health_check():
    """System health endpoint for monitoring"""
    return jsonify({"status": "healthy", "version": "1.1.2"}), 200

@app.route('/api/client', methods=['POST'])
def add_client():
    """Service endpoint to save clients and calculate nutritional targets"""
    data = request.json
    name, weight = data.get('name'), data.get('weight')
    program = data.get('program')

    if not name or program not in programs:
        return jsonify({"error": "Invalid client data"}), 400

    # Specification: weight * calorie_factor
    calories = int(float(weight) * programs[program]["factor"])

    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT OR REPLACE INTO clients (name, weight, program, calories) VALUES (?,?,?,?)",
                    (name, weight, program, calories))
        conn.commit()
        return jsonify({"message": f"Client {name} saved", "calories": calories}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)