import pytest
from app import create_app, db


@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app()
    app.config['TESTING'] = True

    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_token(client):
    """Register and login a test user, return JWT token."""
    # Register
    client.post('/register', json={
        'username': 'pytest_user',
        'email': 'pytest_user@test.com',
        'password': 'password123'
    })

    # Login
    resp = client.post('/auth/login', json={
        'email': 'pytest_user@test.com',
        'password': 'password123'
    })
    data = resp.get_json()
    return data['token']


@pytest.fixture
def auth_headers(auth_token):
    """Return headers with Authorization Bearer token."""
    return {'Authorization': f'Bearer {auth_token}'}
