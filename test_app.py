import pytest
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_add_client_success(client):
    """Verify Muscle Gain Factor: 80kg * 35 = 2800 kcal"""
    payload = {"name": "Farhan", "weight": 80, "program": "Muscle Gain (MG)"}
    response = client.post('/api/client', json=payload)
    assert response.status_code == 201
    assert response.get_json()["calories"] == 2800

def test_invalid_program(client):
    """Ensure system integrity rejects non-specified programs"""
    payload = {"name": "Test", "weight": 70, "program": "Invalid"}
    response = client.post('/api/client', json=payload)
    assert response.status_code == 400