import pytest
from flask import session
from web import create_app

# FIXTURES ---------------------------------------------------

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "LOGIN_DISABLED": True
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

# TESTS ------------------------------------------------------

def test_get_index_page(client):
    response = client.get("/index")
    assert response.request.path == "/index"