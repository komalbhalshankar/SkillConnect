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
                "category": "Programming Languages",
                "icon": "bi-code-slash",
                "description": "Core software development and scripting languages.",
                "skills": [
                    ("Python", "General-purpose programming, scripting, and backend development."),
                    ("Java", "Enterprise application and Android development."),
                    ("C++", "Systems programming, game development, and high-performance computing."),
                    ("JavaScript", "Client and server-side web application programming."),
                    ("TypeScript", "Typed superset of JavaScript for scalable applications."),
                    ("C#", ".NET ecosystem and game development.")
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
                "category": "Data Science & AI",
                "icon": "bi-cpu",
                "description": "Data analysis, machine learning algorithms, and intelligent systems.",
                "skills": [
                    ("Machine Learning", "Supervised, unsupervised algorithms and predictive modeling."),
                    ("Data Analysis with Pandas", "Data cleaning, manipulation, and exploratory data analysis."),
                    ("SQL & Databases", "Relational database querying, optimization, and normalization."),
                    ("Deep Learning", "Neural networks, PyTorch, and computer vision / NLP fundamentals.")
                ]
            },
            {
                "category": "CS Foundations",
                "icon": "bi-diagram-3",
                "description": "Essential theoretical computer science and software architecture.",
                "skills": [
                    ("Data Structures & Algorithms", "Arrays, trees, graphs, sorting, searching, and algorithmic complexity."),
                    ("Operating Systems", "Process management, concurrency, memory allocation, and file systems."),
                    ("Computer Networks", "TCP/IP, HTTP/HTTPS, routing protocols, and network architecture.")
                ]
            },
            {
                "category": "Design & Multimedia",
                "icon": "bi-palette",
                "description": "User experience, visual interfaces, and media creation.",
                "skills": [
                    ("UI/UX Design with Figma", "Wireframing, interactive prototyping, and design systems."),
                    ("Graphic Design", "Vector illustration, brand identity, and typography.")
                ]
            },
            {
                "category": "Communication & Professional",
                "icon": "bi-chat-dots",
                "description": "Interpersonal skills, technical writing, and leadership.",
                "skills": [
                    ("Technical Writing", "Documentation, project reports, and API specifications."),
                    ("Public Speaking", "Presentations, elevator pitches, and seminar delivery.")
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

