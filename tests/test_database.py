"""
Tests for Database Foundation, Models, Constraints, and CLI commands.
"""
import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.user import User
from app.models.skill import SkillCategory, Skill
from app.services.auth_service import AuthService

def test_user_email_unique_database_constraint(app):
    """Verify database-level unique constraint on User.email."""
    with app.app_context():
        user1 = User(
            name="User One",
            email="unique@college.edu",
            password_hash="hash1",
            role="student"
        )
        db.session.add(user1)
        db.session.commit()

        user2 = User(
            name="User Two",
            email="unique@college.edu",  # Duplicate email
            password_hash="hash2",
            role="student"
        )
        db.session.add(user2)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()

def test_skill_category_and_skill_models_relationship(app):
    """
    Verify the minimum skill taxonomy models (SkillCategory & Skill)
    maintain relational integrity with primary and foreign keys.
    """
    with app.app_context():
        cat = SkillCategory(
            name="Programming & Tech",
            description="Software, web, and systems engineering",
            icon="bi-code-slash"
        )
        db.session.add(cat)
        db.session.commit()

        skill = Skill(
            category_id=cat.id,
            name="Python Programming",
            description="Core Python, OOP, and data structures"
        )
        db.session.add(skill)
        db.session.commit()

        # Query back and verify bi-directional relationship
        retrieved_cat = SkillCategory.query.filter_by(name="Programming & Tech").first()
        assert retrieved_cat is not None
        assert len(retrieved_cat.skills) == 1
        assert retrieved_cat.skills[0].name == "Python Programming"
        assert retrieved_cat.skills[0].category.name == "Programming & Tech"

def test_cli_init_db(cli_runner):
    """Verify 'flask init-db' CLI command executes safely."""
    result = cli_runner.invoke(args=['init-db'])
    assert result.exit_code == 0
    assert "Database tables initialized successfully" in result.output

def test_cli_create_admin(cli_runner, app):
    """Verify 'flask create-admin' CLI command securely creates an administrator."""
    result = cli_runner.invoke(args=[
        'create-admin',
        '--name', 'Dr. Ramesh Kumar',
        '--email', 'ramesh.admin@college.edu',
        '--password', 'AdminSecretPass2026'
    ])
    assert result.exit_code == 0
    assert "Administrator account 'ramesh.admin@college.edu' created successfully" in result.output

    with app.app_context():
        admin = User.query.filter_by(email='ramesh.admin@college.edu').first()
        assert admin is not None
        assert admin.role == 'admin'
        assert admin.name == 'Dr. Ramesh Kumar'
        assert admin.check_password('AdminSecretPass2026') is True
