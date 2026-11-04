import pytest
from app.services.auth_service import AuthService

def test_auth_success(client):
    """Test successful authentication with valid credentials."""
    user, err = AuthService.authenticate('admin', 'Admin@123')
    assert err is None
    assert user is not None
    assert user['username'] == 'admin'
    assert user['role_name'] == 'ADMIN'

def test_auth_invalid_credentials():
    """Test authentication failure with incorrect password."""
    user, err = AuthService.authenticate('admin', 'WrongPassword!99')
    assert user is None
    assert "Invalid password" in err or "locked" in err

def test_login_logout_flow(client):
    """Test full web login and logout lifecycle."""
    # 1. Login
    res = client.post('/login', data={'username': 'admin', 'password': 'Admin@123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Dashboard" in res.data

    # 2. Logout
    res_logout = client.get('/logout', follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"logged out successfully" in res_logout.data

def test_role_based_access_control(client):
    """Test RBAC enforcement: Student role is rejected from admin database management."""
    # Login as student
    client.post('/login', data={'username': 'john_doe', 'password': 'Student@123'}, follow_redirects=True)
    
    # Attempt to access admin database management page
    res = client.get('/database-management', follow_redirects=True)
    assert res.status_code == 200
    assert b"Access Denied" in res.data

