"""
Application factory for SkillConnect.
"""
import os
from datetime import datetime, timezone
from pathlib import Path
from flask import Flask, render_template
from app.config import config_by_name
from app.extensions import db, login_manager, csrf

def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application instance."""
    app = Flask(__name__, instance_relative_config=True)

    # Determine configuration
    if not config_name:
        config_name = os.getenv('FLASK_ENV', 'development')
    config_class = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(config_class)

    # Ensure instance directory exists
    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.skills import skills_bp
    from app.routes.matching import matching_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(matching_bp)

    # Register CLI Commands
    from app.cli import register_cli_commands
    register_cli_commands(app)

    # Global context processors for templates
    @app.context_processor
    def inject_global_data():
        return {
            'current_year': datetime.now(timezone.utc).year
        }

    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    return app
