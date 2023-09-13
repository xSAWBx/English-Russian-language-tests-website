# tests/test_app.py

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome to the Quiz App' in response.data

def test_start_quiz_route(client):
    response = client.get('/quiz/start')
    assert response.status_code == 200
    assert b'Start the Quiz' in response.data