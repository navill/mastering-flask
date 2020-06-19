from main import app


def test_user():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200

