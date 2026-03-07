import pytest
from app import app, init_db

@pytest.fixture
def client():
    """Configures the platform for an isolated test environment"""
    app.config['TESTING'] = True
    init_db()  # Ensure tables exist before each test
    with app.test_client() as client:
        yield client

# --- 1. Client Management Tests ---
def test_save_client_math(client):
    """Verify MG calorie math: 80kg * 35 factor = 2800 kcal"""
    payload = {"name": "Farhan", "age": 25, "weight": 80, "program": "Muscle Gain (MG)"}
    response = client.post('/api/client', json=payload)
    assert response.status_code == 201
    assert response.get_json()["calories"] == 2800

def test_save_client_invalid_program(client):
    """Ensure system integrity rejects non-baseline programs"""
    payload = {"name": "Test", "weight": 70, "program": "Invalid Program"}
    response = client.post('/api/client', json=payload)
    assert response.status_code == 400

# --- 2. Progress & Relational Tests ---
def test_save_progress_log(client):
    """Verify that weekly adherence can be logged successfully"""
    payload = {"name": "Farhan", "adherence": 95}
    response = client.post('/api/progress', json=payload)
    assert response.status_code == 201
    assert "Week" in response.get_json()["week"]

# --- 3. Visualization API Tests (v2.2.1 Evolution) ---
def test_get_progress_history_ordered(client):
    """Verify relational retrieval for Matplotlib visualization"""
    # Create a history of progress logs
    client.post('/api/progress', json={"name": "Farhan", "adherence": 80})
    client.post('/api/progress', json={"name": "Farhan", "adherence": 90})
    
    # Retrieve history for the chart
    response = client.get('/api/progress/Farhan')
    data = response.get_json()
    
    assert response.status_code == 200
    assert len(data) == 2  # Verify system returned both logs
    assert data[1]["adherence"] == 90  # Ensure data integrity

def test_get_progress_no_data(client):
    """Ensure API handles empty historical records gracefully"""
    response = client.get('/api/progress/NewUser')
    assert response.status_code == 200
    assert response.get_json() == []  # Should return an empty list for visualization