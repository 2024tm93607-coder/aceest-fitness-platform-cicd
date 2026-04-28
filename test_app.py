import pytest
import os
from app import app, init_db, DB_NAME

API_CLIENT_ENDPOINT = '/api/client'
API_WORKOUT_ENDPOINT = '/api/workout'
API_LOGIN_ENDPOINT = '/api/login'
API_PROGRESS_ENDPOINT = '/api/progress'

@pytest.fixture
def client():
    if os.path.exists(DB_NAME): os.remove(DB_NAME) 
    app.config['TESTING'] = True
    init_db() 
    with app.test_client() as client: yield client
    if os.path.exists(DB_NAME): os.remove(DB_NAME)

def test_dashboard_home(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b"ACEest Platform - Dashboard" in res.data

def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    assert res.get_json()["version"] == "3.2.4"

def test_login_success(client):
    res = client.post(API_LOGIN_ENDPOINT, json={"username": "admin", "password": "admin"}) # NOSONAR
    assert res.status_code == 200
    assert res.get_json()["role"] == "Admin"

def test_login_failure(client):
    res = client.post(API_LOGIN_ENDPOINT, json={"username": "admin", "password": "wrong"}) # NOSONAR
    assert res.status_code == 401

def test_client_creation_and_math(client):
    res = client.post(API_CLIENT_ENDPOINT, json={"name": "Farhan", "weight": 80, "program": "Muscle Gain"})
    assert res.status_code == 201
    assert res.get_json()["calories"] == 2800

def test_invalid_client_rejection(client):
    res = client.post(API_CLIENT_ENDPOINT, json={"name": "Test", "weight": 70, "program": "Yoga"})
    assert res.status_code == 400

def test_client_membership_persistence(client):
    res = client.post(API_CLIENT_ENDPOINT, json={"name": "Farhan", "weight": 80, "program": "Beginner", "membership_status": "Active", "membership_end": "2026-12-31"})
    assert res.status_code == 201

def test_membership_retrieval(client):
    client.post(API_CLIENT_ENDPOINT, json={"name": "Farhan", "weight": 80, "program": "Muscle Gain", "membership_status": "Active", "membership_end": "2026-12-31"})
    res = client.get('/api/membership/Farhan')
    assert res.status_code == 200
    assert res.get_json()["status"] == "Active"

def test_bmi_and_risk_logic(client):
    client.post(API_CLIENT_ENDPOINT, json={"name": "Farhan", "height": 175, "weight": 75, "program": "Beginner"})
    res = client.get('/api/bmi/Farhan')
    assert res.status_code == 200
    assert res.get_json()["bmi"] == 24.5

def test_bmi_missing_data(client):
    res = client.get('/api/bmi/UnknownUser')
    assert res.status_code == 404

def test_body_metrics_persistence(client):
    res = client.post('/api/metrics', json={"name": "Farhan", "weight": 74.5, "waist": 82.5, "bodyfat": 14.5})
    assert res.status_code == 201

def test_history_retrieval_isolation(client):
    client.post(API_PROGRESS_ENDPOINT, json={"name": "Farhan", "adherence": 85})
    client.post(API_PROGRESS_ENDPOINT, json={"name": "Farhan", "adherence": 92})
    res = client.get('/api/progress/Farhan')
    assert len(res.get_json()) == 2

def test_log_workout_with_exercise(client):
    res = client.post(API_WORKOUT_ENDPOINT, json={
        "name": "Farhan", "type": "Hypertrophy", "duration": 45, "notes": "Felt good",
        "ex_name": "Bench Press", "ex_sets": 3, "ex_reps": 10, "ex_weight": 60
    })
    assert res.status_code == 201
    assert "workout_id" in res.get_json()

def test_log_workout_missing_data(client):
    res = client.post(API_WORKOUT_ENDPOINT, json={"name": "Farhan"})
    assert res.status_code == 400

def test_get_workout_history_ordering(client):
    client.post(API_WORKOUT_ENDPOINT, json={"name": "Farhan", "date": "2026-03-01", "type": "Strength"})
    client.post(API_WORKOUT_ENDPOINT, json={"name": "Farhan", "date": "2026-03-05", "type": "Conditioning"})
    res = client.get('/api/workouts/Farhan')
    assert res.get_json()[0]["date"] == "2026-03-05"

def test_ai_program_generation(client):
    client.post(API_CLIENT_ENDPOINT, json={"name": "Farhan", "weight": 80, "program": "Beginner"})
    res = client.post('/api/program/generate', json={"name": "Farhan", "focus": "Fat Loss"})
    assert res.status_code == 200
    assert "program" in res.get_json()

def test_pdf_report_generation(client):
    client.post(API_CLIENT_ENDPOINT, json={"name": "Farhan", "weight": 80, "program": "Beginner"})
    res = client.get('/api/report/Farhan')
    assert res.status_code == 200
    assert res.headers["Content-Type"] == "application/pdf"