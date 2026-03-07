import pytest
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_full_client_lifecycle(client):
    """Verify dual-table persistence for clients and weekly logs"""
    # 1. Save Client
    res1 = client.post('/api/client', json={"name": "Farhan", "age": 25, "weight": 80, "program": "Muscle Gain (MG)"})
    assert res1.status_code == 201
    
    # 2. Log Progress
    res2 = client.post('/api/progress', json={"name": "Farhan", "adherence": 90})
    assert res2.status_code == 201
    assert "Week" in res2.get_json()["week"]