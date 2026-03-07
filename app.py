from flask import Flask, jsonify

app = Flask(__name__)

# Logic from Aceestver-1.0.py
programs = {
    "Fat Loss (FL)": {"target": "2,000 kcal", "color": "#e74c3c"},
    "Muscle Gain (MG)": {"target": "3,200 kcal", "color": "#2ecc71"},
    "Beginner (BG)": {"target": "120g protein/day", "color": "#3498db"}
}

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "version": "1.0"}), 200

@app.route('/api/programs', methods=['GET'])
def get_programs():
    return jsonify(programs), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)