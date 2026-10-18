"""
CLI commands for safe database initialization and administrator management.
"""
import click
from app.extensions import db
from app.models.user import User
from app.services.auth_service import AuthService

def register_cli_commands(app):
    """Register custom CLI commands with the Flask application."""

    @app.cli.command("init-db")
    def init_db():
        """Safe database initialization. Creates all tables idempotently without deleting existing data."""
        with app.app_context():
            db.create_all()
            click.echo("[SUCCESS] Database tables initialized successfully (existing tables and data preserved).")

    @app.cli.command("create-admin")
    @click.option("--name", prompt="Admin Full Name", default="System Administrator", help="Admin's display name.")
    @click.option("--email", prompt="Admin Email Address", help="Admin's login email.")
    @click.option("--password", prompt="Admin Password", hide_input=True, confirmation_prompt=True, help="Secure password.")
    def create_admin(name, email, password):
        """Safely create an initial administrator account via CLI without hardcoding credentials."""
        with app.app_context():
            db.create_all()

            existing = User.query.filter_by(email=email.strip().lower()).first()
            if existing:
                if existing.role == 'admin':
                    click.echo(f"[INFO] An administrator account with email '{email}' already exists.")
                else:
                    existing.role = 'admin'
                    db.session.commit()
                    click.echo(f"[SUCCESS] Existing user '{email}' was promoted to Administrator role.")
                return

            user, error = AuthService.register_user(
                name=name,
                email=email,
                password=password,
                role='admin',
                bio='SkillConnect System Administrator'
            )
            if error:
                click.echo(f"[ERROR] Failed to create administrator: {error}")
            else:
                click.echo(f"[SUCCESS] Administrator account '{user.email}' created successfully.")
