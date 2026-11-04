import os
import sys
from pathlib import Path
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app
from app.database.connection import db_manager, Base
from scripts.init_db import initialize_database

@pytest.fixture(scope='session')
def app():
    # Use testing config with isolated SQLite test database
    test_app = create_app('testing')
    test_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Initialize test schema and seed data
    initialize_database()
    
    yield test_app

@pytest.fixture(scope='session')
def client(app):
    return app.test_client()

@pytest.fixture
def auth_admin(client):
    """Helper to log in as ADMIN."""
    client.post('/login', data={'username': 'admin', 'password': 'Admin@123'}, follow_redirects=True)
    return client

@pytest.fixture
def auth_faculty(client):
    """Helper to log in as FACULTY."""
    client.post('/login', data={'username': 'prof_smith', 'password': 'Faculty@123'}, follow_redirects=True)
    return client

@pytest.fixture
def auth_student(client):
    """Helper to log in as STUDENT."""
    client.post('/login', data={'username': 'john_doe', 'password': 'Student@123'}, follow_redirects=True)
    return client

