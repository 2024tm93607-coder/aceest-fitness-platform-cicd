import pytest
import os
from app import app, init_db, DB_NAME

@pytest.fixture
def client():
    """Provides a fresh, isolated database for every individual test"""
    # 1. PRE-TEST: Wipe any existing database file to ensure a clean start
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME) 
    
    app.config['TESTING'] = True
    init_db()  # Re-initialize the relational schema
    
    with app.test_client() as client:
        yield client
    
    # 2. POST-TEST: Clean up to prevent state leaks into subsequent tests
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

# --- 1. Client & Logic Validation ---
def test_save_client_math(client):
    """Verify MG calorie math: 80kg * 35 factor = 2800 kcal"""
    payload = {"name": "Farhan", "age": 25, "weight": 80, "program": "Muscle Gain (MG)"}
    response = client.post('/api/client', json=payload)
    assert response.status_code == 201
    assert response.get_json()["calories"] == 2800

def test_invalid_program_rejection(client):
    """Ensure system integrity rejects non-baseline programs"""
    payload = {"name": "Test", "weight": 70, "program": "Invalid"}
    response = client.post('/api/client', json=payload)
    assert response.status_code == 400

# --- 2. Progress & Relational Logging ---
def test_save_progress_log(client):
    """Verify that weekly adherence is logged with date metadata"""
    payload = {"name": "Farhan", "adherence": 95}
    response = client.post('/api/progress', json=payload)
    assert response.status_code == 201
    assert "Week" in response.get_json()["week"]

# --- 3. Visualization API Validation ---
def test_get_progress_history_ordered(client):
    """Verify relational retrieval for Matplotlib visualization"""
    # This now starts with 0 records due to the fixture isolation
    client.post('/api/progress', json={"name": "Farhan", "adherence": 80})
    client.post('/api/progress', json={"name": "Farhan", "adherence": 90})
    
    response = client.get('/api/progress/Farhan')
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) == 2  # This will now correctly pass
    assert data[1]["adherence"] == 90

def test_get_progress_no_data(client):
    """Ensure API handles empty records gracefully for the UI"""
    response = client.get('/api/progress/NewUser')
    assert response.status_code == 200
    assert response.get_json() == []