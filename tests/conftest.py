"""
Pytest configuration and test fixtures for SkillConnect.
All tests run against an isolated in-memory SQLite database.
"""
import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.services.auth_service import AuthService

@pytest.fixture
def app():
    """Create a test application instance configured with an in-memory SQLite database."""
    app_instance = create_app('testing')
    
    with app_instance.app_context():
        db.create_all()
        yield app_instance
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for making HTTP requests."""
    return app.test_client()

@pytest.fixture
def cli_runner(app):
    """A test runner for Flask CLI commands."""
    return app.test_cli_runner()

@pytest.fixture
def student_user(app):
    """Create and return a sample registered student."""
    user, _ = AuthService.register_user(
        name="Aarav Sharma",
        email="aarav@college.edu",
        password="securePassword123",
        college="Dept of Computer Science, National Institute",
        bio="Aspiring software engineer interested in systems programming.",
        availability="Weekday evenings",
        role="student"
    )
    return user

@pytest.fixture
def second_student_user(app):
    """Create and return a second distinct registered student."""
    user, _ = AuthService.register_user(
        name="Priya Patel",
        email="priya@college.edu",
        password="priyaPassword456",
        college="School of Design, Tech University",
        bio="UI/UX design enthusiast.",
        availability="Weekends only",
        role="student"
    )
    return user

@pytest.fixture
def admin_user(app):
    """Create and return an administrator user."""
    user, _ = AuthService.register_user(
        name="Prof. Verma",
        email="admin@college.edu",
        password="adminSecretPassword789",
        college="Department of Computer Applications",
        bio="Department Coordinator & Platform Moderator",
        availability="Campus hours",
        role="admin"
    )
    return user

@pytest.fixture
def auth_client(client, student_user):
    """Test client authenticated as student_user."""
    client.post('/auth/login', data={
        'email': 'aarav@college.edu',
        'password': 'securePassword123'
    }, follow_redirects=True)
    return client

@pytest.fixture
def admin_client(client, admin_user):
    """Test client authenticated as admin_user."""
    client.post('/auth/login', data={
        'email': 'admin@college.edu',
        'password': 'adminSecretPassword789'
    }, follow_redirects=True)
    return client
