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

    @app.cli.command("seed-skills")
    def seed_skills():
        """Idempotently seed standard academic categories and skills."""
        from app.models.skill import SkillCategory, Skill
        from app.services.skill_service import SkillService

        sample_data = [
            {
                "category": "Programming",
                "icon": "bi-code-slash",
                "description": "Core programming languages, algorithms, and software development.",
                "skills": [
                    ("Python", "General-purpose programming, scripting, and backend development."),
                    ("Java", "Enterprise application and Android development."),
                    ("C++", "Systems programming, game development, and high-performance computing."),
                    ("JavaScript", "Client and server-side web application programming."),
                    ("Data Structures & Algorithms", "Arrays, trees, graphs, sorting, and algorithmic complexity.")
                ]
            },
            {
                "category": "Database",
                "icon": "bi-database",
                "description": "Relational databases, SQL optimization, and data modeling.",
                "skills": [
                    ("SQL & Relational Databases", "Relational querying, schema design, and ACID transactions."),
                    ("PostgreSQL", "Advanced open-source relational database management."),
                    ("MongoDB", "Document-oriented NoSQL database for unstructured data."),
                    ("Database Design & Normalization", "ER diagrams, normal forms (1NF to BCNF), and indexing.")
                ]
            },
            {
                "category": "Web Development",
                "icon": "bi-globe",
                "description": "Frontend, backend, and full-stack web engineering.",
                "skills": [
                    ("HTML5 & CSS3", "Modern responsive markup, flexbox, and grid layouts."),
                    ("React", "Component-based frontend UI library."),
                    ("Flask", "Lightweight Python web microframework."),
                    ("Django", "High-level Python web framework for rapid development."),
                    ("Node.js", "Server-side JavaScript runtime environment.")
                ]
            },
            {
                "category": "Design",
                "icon": "bi-palette",
                "description": "UI/UX design, visual prototyping, and graphic design.",
                "skills": [
                    ("UI/UX Design with Figma", "Wireframing, interactive prototyping, and design systems."),
                    ("Graphic Design", "Vector illustration, brand identity, and typography.")
                ]
            },
            {
                "category": "Communication",
                "icon": "bi-chat-dots",
                "description": "Interpersonal skills, technical writing, and presentation.",
                "skills": [
                    ("Technical Writing", "Documentation, project reports, and API specifications."),
                    ("Public Speaking", "Presentations, elevator pitches, and seminar delivery.")
                ]
            },
            {
                "category": "Other",
                "icon": "bi-tags",
                "description": "General academic subjects and miscellaneous skills.",
                "skills": [
                    ("Machine Learning", "Supervised, unsupervised algorithms and predictive modeling."),
                    ("Operating Systems", "Process management, concurrency, memory allocation, and file systems."),
                    ("Computer Networks", "TCP/IP, HTTP/HTTPS, routing protocols, and network architecture.")
                ]
            }
        ]

        with app.app_context():
            db.create_all()
            total_cats = 0
            total_skills = 0

            for cat_data in sample_data:
                category = SkillCategory.query.filter_by(name=cat_data["category"]).first()
                if not category:
                    category = SkillCategory(
                        name=cat_data["category"],
                        icon=cat_data["icon"],
                        description=cat_data["description"]
                    )
                    db.session.add(category)
                    db.session.flush()
                    total_cats += 1

                for skill_name, skill_desc in cat_data["skills"]:
                    skill = Skill.query.filter_by(name=skill_name).first()
                    if not skill:
                        skill = Skill(
                            category_id=category.id,
                            name=skill_name,
                            description=skill_desc
                        )
                        db.session.add(skill)
                        total_skills += 1

            db.session.commit()
            click.echo(f"[SUCCESS] Skills seeding complete: {total_cats} categories added, {total_skills} skills added.")

