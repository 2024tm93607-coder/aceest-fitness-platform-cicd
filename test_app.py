import pytest
import os
from app import app, init_db, DB_NAME

@pytest.fixture
def client():
    """Ensures absolute database isolation for testing to prevent state contamination."""
    if os.path.exists(DB_NAME): os.remove(DB_NAME) 
    app.config['TESTING'] = True
    init_db() 
    with app.test_client() as client: yield client
    if os.path.exists(DB_NAME): os.remove(DB_NAME)

# --- 0. System Tests ---
def test_health_check(client):
    """Verify system is online and running the correct version."""
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json()["version"] == "3.0.1"

# --- 1. Client & Calorie Logic ---
def test_client_creation_and_math(client):
    """Verify MG-PPL factor (35): 80kg * 35 = 2800 kcal."""
    res = client.post('/api/client', json={"name": "Farhan", "weight": 80, "program": "Muscle Gain (MG) – PPL"})
    assert res.status_code == 201
    assert res.get_json()["calories"] == 2800

def test_invalid_client_rejection(client):
    """Ensure system rejects invalid programs to maintain data integrity."""
    res = client.post('/api/client', json={"name": "Test", "weight": 70, "program": "Yoga"})
    assert res.status_code == 400

# --- 2. Advanced Metrics & BMI Analytics ---
def test_bmi_and_risk_logic(client):
    """Verify BMI calculation and categorization."""
    client.post('/api/client', json={"name": "Farhan", "height": 175, "weight": 75, "program": "Beginner (BG)"})
    res = client.get('/api/bmi/Farhan')
    assert res.status_code == 200
    data = res.get_json()
    assert data["bmi"] == 24.5
    assert data["category"] == "Normal"

def test_bmi_missing_data(client):
    """Ensure BMI handles missing client data gracefully with a 404."""
    res = client.get('/api/bmi/UnknownUser')
    assert res.status_code == 404

def test_body_metrics_persistence(client):
    """Verify relational storage for body measurements."""
    res = client.post('/api/metrics', json={"name": "Farhan", "weight": 74.5, "waist": 82.5, "bodyfat": 14.5})
    assert res.status_code == 201

# --- 3. Progress Integrity ---
def test_history_retrieval_isolation(client):
    """Verify API returns a valid list and confirms zero state contamination."""
    client.post('/api/progress', json={"name": "Farhan", "adherence": 85})
    client.post('/api/progress', json={"name": "Farhan", "adherence": 92})
    res = client.get('/api/progress/Farhan')
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 2
    assert data[1]["adherence"] == 92

# --- 4. NEW v3.0.1 Workout & Exercise Tests ---
def test_log_workout_with_exercise(client):
    """Verify dual-table insertion for workouts and exercises."""
    res = client.post('/api/workout', json={
        "name": "Farhan", "type": "Hypertrophy", "duration": 45, "notes": "Felt good",
        "ex_name": "Bench Press", "ex_sets": 3, "ex_reps": 10, "ex_weight": 60
    })
    assert res.status_code == 201
    assert "workout_id" in res.get_json()

def test_log_workout_missing_data(client):
    """Verify validation rejects workouts missing a defined type."""
    res = client.post('/api/workout', json={"name": "Farhan"})
    assert res.status_code == 400

def test_get_workout_history_ordering(client):
    """Verify history is retrieved and ordered by Date DESC for the UI."""
    client.post('/api/workout', json={"name": "Farhan", "date": "2026-03-01", "type": "Strength"})
    client.post('/api/workout', json={"name": "Farhan", "date": "2026-03-05", "type": "Conditioning"})
    
    res = client.get('/api/workouts/Farhan')
    data = res.get_json()
    assert res.status_code == 200
    assert len(data) == 2
    assert data[0]["date"] == "2026-03-05" # Ensures descending order