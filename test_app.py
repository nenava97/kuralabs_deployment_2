from application import app

def test_home_page():
    response = app.test_client().get('/')
    assert response.status_code == 200

def test_home_page():
    response = app.test_client().post('/')
    assert response.status_code == 405
