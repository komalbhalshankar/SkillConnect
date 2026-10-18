"""
Tests for Module 1: User Authentication & Role-Based Access Control.
"""
from app.models.user import User
from app.services.auth_service import AuthService

def test_successful_student_registration(client, app):
    """Test successful student registration flow."""
    response = client.post('/auth/register', data={
        'name': 'Kavya Singh',
        'email': 'kavya@college.edu',
        'password': 'password123',
        'confirm_password': 'password123',
        'college': 'Institute of Engineering',
        'bio': 'Passionate about algorithms and web development.',
        'availability': 'Saturday and Sunday'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your account has been created successfully" in response.data

    with app.app_context():
        user = User.query.filter_by(email='kavya@college.edu').first()
        assert user is not None
        assert user.name == 'Kavya Singh'
        assert user.role == 'student'
        assert user.college == 'Institute of Engineering'
        assert user.password_hash != 'password123'  # Must be hashed!
        assert user.check_password('password123') is True

def test_duplicate_email_registration_rejected(client, student_user):
    """Test that registering with an existing email is rejected with a clear message."""
    response = client.post('/auth/register', data={
        'name': 'Imposter User',
        'email': 'aarav@college.edu',  # Same email as student_user
        'password': 'differentPassword',
        'confirm_password': 'differentPassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"An account with this email address already exists" in response.data

def test_password_hashing_security(app):
    """Verify passwords are salted and hashed; plaintext is never stored."""
    user, _ = AuthService.register_user(
        name="Security Test",
        email="security@college.edu",
        password="plainTextSecret99"
    )

    assert user.password_hash is not None
    assert "plainTextSecret99" not in user.password_hash
    assert user.password_hash.startswith("scrypt:") or user.password_hash.startswith("pbkdf2:")
    assert user.check_password("plainTextSecret99") is True
    assert user.check_password("wrongPassword") is False

def test_successful_login(client, student_user):
    """Test student login with valid credentials."""
    response = client.post('/auth/login', data={
        'email': 'aarav@college.edu',
        'password': 'securePassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Welcome back, Aarav Sharma!" in response.data
    assert b"Logout" in response.data

def test_unsuccessful_login_with_wrong_password(client, student_user):
    """Test login rejection when password does not match."""
    response = client.post('/auth/login', data={
        'email': 'aarav@college.edu',
        'password': 'wrongPassword123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_unsuccessful_login_with_unregistered_email(client):
    """Test login rejection when email does not exist."""
    response = client.post('/auth/login', data={
        'email': 'nonexistent@college.edu',
        'password': 'anyPassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Invalid email or password" in response.data

def test_logout(auth_client):
    """Test user logout clears the session."""
    response = auth_client.get('/auth/logout', follow_redirects=True)

    assert response.status_code == 200
    assert b"You have been logged out securely" in response.data
    assert b"Sign In" in response.data

def test_protected_routes_redirect_unauthenticated_user(client):
    """Verify that unauthenticated users are redirected to login for protected pages."""
    protected_urls = ['/dashboard', '/profile']
    for url in protected_urls:
        response = client.get(url, follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.headers['Location']

def test_admin_access_allowed_for_admin_role(admin_client):
    """Verify that users with role 'admin' can access /admin."""
    response = admin_client.get('/admin')
    assert response.status_code == 200
    assert b"Administrator Portal" in response.data

def test_admin_access_forbidden_for_student_role(auth_client):
    """Verify that regular students receive an HTTP 403 Forbidden on /admin."""
    response = auth_client.get('/admin')
    assert response.status_code == 403
    assert b"403" in response.data
