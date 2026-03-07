import pytest
import os
from app import app, init_db, DB_NAME

@pytest.fixture
def client():
    """Ensures a fresh, isolated database for every individual test to prevent state contamination."""
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME) 
    app.config['TESTING'] = True
    init_db() 
    with app.test_client() as client:
        yield client
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

# --- 1. Client Management & Calculation Logic ---
def test_muscle_gain_math(client):
    """Verify MG-PPL factor (35): 80kg * 35 = 2800 kcal."""
    res = client.post('/api/client', json={
        "name": "Farhan", "weight": 80, "program": "Muscle Gain (MG) – PPL"
    })
    assert res.status_code == 201
    assert res.get_json()["calories"] == 2800

def test_fat_loss_5day_math(client):
    """Verify FL-5day factor (24): 100kg * 24 = 2400 kcal."""
    res = client.post('/api/client', json={
        "name": "User2", "weight": 100, "program": "Fat Loss (FL) – 5 day"
    })
    assert res.get_json()["calories"] == 2400

def test_invalid_program_rejection(client):
    """Ensure system integrity rejects non-baseline programs."""
    res = client.post('/api/client', json={"name": "Test", "weight": 70, "program": "Yoga"})
    assert res.status_code == 400

# --- 2. Advanced Metrics & BMI Analytics ---
def test_bmi_and_risk_logic(client):
    """Verify BMI calculation: 175cm, 75kg = 24.5 (Normal category)."""
    client.post('/api/client', json={
        "name": "Farhan", "height": 175, "weight": 75, "program": "Beginner (BG)"
    })
    res = client.get('/api/bmi/Farhan')
    data = res.get_json()
    assert res.status_code == 200
    assert data["bmi"] == 24.5
    assert data["category"] == "Normal"

def test_body_metrics_persistence(client):
    """Verify relational storage for bodyfat and waist metrics."""
    res = client.post('/api/metrics', json={
        "name": "Farhan", "weight": 74.5, "waist": 82.5, "bodyfat": 14.5
    })
    assert res.status_code == 201

# --- 3. Progress & Visualization Integrity ---
def test_history_retrieval_isolation(client):
    """Verify API returns a valid list for Matplotlib and confirms zero state contamination."""
    client.post('/api/progress', json={"name": "Farhan", "adherence": 85})
    client.post('/api/progress', json={"name": "Farhan", "adherence": 92})
    
    res = client.get('/api/progress/Farhan')
    data = res.get_json()
    
    assert res.status_code == 200
    assert data is not None  # Fix for previous NoneType error
    assert len(data) == 2
    assert data[1]["adherence"] == 92