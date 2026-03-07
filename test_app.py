import pytest
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_save_client_and_progress(client):
    """Verify dual-table integrity"""
    # 1. Save Client
    c_res = client.post('/api/client', json={"name": "Farhan", "weight": 80, "program": "Muscle Gain (MG)", "age": 25})
    assert c_res.status_code == 201
    
    # 2. Log Progress
    p_res = client.post('/api/progress', json={"name": "Farhan", "adherence": 95})
    assert p_res.status_code == 201
    assert "Week" in p_res.get_json()["week"]