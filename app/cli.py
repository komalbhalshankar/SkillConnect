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

    @app.cli.command("seed-demo")
    def seed_demo():
        """
        Idempotently populate rich demonstration data exercising all five modules:
        - Standard categories and skills taxonomy
        - 1 Administrator account (admin@college.edu / Admin@123)
        - 4 Student accounts (aarav, priya, rohan, ananya @college.edu / Student@123)
        - Complementary teach and learn portfolios
        - Reciprocal and one-way match relationships
        - Exchange proposals in pending, accepted, rejected, and cancelled states
        - Scheduled upcoming, completed, and cancelled learning sessions
        - Post-session ratings and qualitative peer reviews
        """
        from datetime import datetime, timezone, timedelta
        from app.models.skill import SkillCategory, Skill, UserSkill
        from app.models.exchange import ExchangeRequest, ExchangeSession
        from app.models.rating import Rating

        with app.app_context():
            db.create_all()

            # 1. Ensure Standard Taxonomy is Seeded
            click.echo("[1/5] Ensuring standard skills taxonomy is present...")
            # Run existing seed_skills logic
            categories_def = [
                ("Programming", "bi-code-slash", "Core programming languages and algorithms.", [
                    ("Python", "General-purpose programming and backend development."),
                    ("Java", "Enterprise application and Android development."),
                    ("C++", "Systems programming and high-performance computing."),
                    ("JavaScript", "Client and server-side web application programming."),
                    ("Data Structures & Algorithms", "Algorithmic problem solving and complexity.")
                ]),
                ("Database", "bi-database", "Relational databases and data modeling.", [
                    ("SQL & Relational Databases", "Relational querying and schema normalization."),
                    ("PostgreSQL", "Advanced open-source relational database management.")
                ]),
                ("Web Development", "bi-globe", "Frontend and full-stack web engineering.", [
                    ("HTML5 & CSS3", "Modern responsive markup, flexbox, and grid layouts."),
                    ("React", "Component-based frontend UI library."),
                    ("Flask", "Lightweight Python web microframework.")
                ]),
                ("Design", "bi-palette", "UI/UX design and visual prototyping.", [
                    ("UI/UX Design with Figma", "Wireframing, interactive prototyping, and design systems."),
                    ("Graphic Design", "Vector illustration and typography.")
                ]),
                ("Other", "bi-tags", "General academic and technical subjects.", [
                    ("Machine Learning", "Supervised, unsupervised models and data analysis.")
                ])
            ]

            skill_lookup = {}
            for cat_name, icon, desc, skills in categories_def:
                cat = SkillCategory.query.filter_by(name=cat_name).first()
                if not cat:
                    cat = SkillCategory(name=cat_name, icon=icon, description=desc)
                    db.session.add(cat)
                    db.session.flush()
                for s_name, s_desc in skills:
                    sk = Skill.query.filter_by(name=s_name).first()
                    if not sk:
                        sk = Skill(category_id=cat.id, name=s_name, description=s_desc)
                        db.session.add(sk)
                        db.session.flush()
                    skill_lookup[s_name] = sk

            db.session.commit()

            # 2. Seed Admin and Student Accounts
            click.echo("[2/5] Seeding demo user accounts...")
            admin_user = User.query.filter_by(email="admin@college.edu").first()
            if not admin_user:
                admin_user, _ = AuthService.register_user(
                    name="Prof. Sharma (Admin)",
                    email="admin@college.edu",
                    password="Admin@123",
                    role="admin",
                    college="Department of Computer Applications",
                    bio="Platform Administrator & Academic Coordinator"
                )

            students_spec = [
                ("Aarav Sharma", "aarav@college.edu", "National Institute of Technology", "CS major passionate about backend architecture and Python.", "Weekday evenings"),
                ("Priya Patel", "priya@college.edu", "School of Design, Tech University", "Design student specializing in Figma wireframes and product UX.", "Weekends & Tuesday"),
                ("Rohan Gupta", "rohan@college.edu", "Institute of Science & Technology", "Data enthusiast and competitive programmer.", "Flexible"),
                ("Ananya Iyer", "ananya@college.edu", "College of Engineering", "Frontend web developer exploring distributed systems.", "Mon, Wed, Fri")
            ]

            students = {}
            for name, email, college, bio, avail in students_spec:
                u = User.query.filter_by(email=email).first()
                if not u:
                    u, _ = AuthService.register_user(
                        name=name,
                        email=email,
                        password="Student@123",
                        role="student",
                        college=college,
                        bio=bio,
                        availability=avail
                    )
                students[email] = u

            db.session.commit()

            # 3. Seed Skill Portfolios
            click.echo("[3/5] Seeding student skill portfolios...")
            def add_user_skill_safe(user, skill_name, stype, prof, notes):
                sk = skill_lookup.get(skill_name)
                if not sk:
                    return
                existing = UserSkill.query.filter_by(user_id=user.id, skill_id=sk.id, skill_type=stype).first()
                if not existing:
                    us = UserSkill(user_id=user.id, skill_id=sk.id, skill_type=stype, proficiency=prof, notes=notes)
                    db.session.add(us)

            # Aarav: Teaches Python (Adv), SQL (Int); Learns UI/UX (Beg), ML (Beg)
            add_user_skill_safe(students["aarav@college.edu"], "Python", "teach", "advanced", "Experienced in Flask, algorithms, and backend APIs.")
            add_user_skill_safe(students["aarav@college.edu"], "SQL & Relational Databases", "teach", "intermediate", "Database design and query tuning.")
            add_user_skill_safe(students["aarav@college.edu"], "UI/UX Design with Figma", "learn", "beginner", "Want to learn Figma prototyping for web apps.")
            add_user_skill_safe(students["aarav@college.edu"], "Machine Learning", "learn", "beginner", "Exploring scikit-learn and classification.")

            # Priya: Teaches UI/UX (Adv), Graphic Design (Int); Learns Python (Int), HTML/CSS (Beg)
            add_user_skill_safe(students["priya@college.edu"], "UI/UX Design with Figma", "teach", "advanced", "Experienced with Figma component systems and user research.")
            add_user_skill_safe(students["priya@college.edu"], "Graphic Design", "teach", "intermediate", "Typography and vector layouts.")
            add_user_skill_safe(students["priya@college.edu"], "Python", "learn", "intermediate", "Looking to build automated scripts.")
            add_user_skill_safe(students["priya@college.edu"], "HTML5 & CSS3", "learn", "beginner", "Connecting Figma mockups with code.")

            # Rohan: Teaches ML (Adv), DSA (Adv); Learns Python (Int)
            add_user_skill_safe(students["rohan@college.edu"], "Machine Learning", "teach", "advanced", "Neural nets, regression, and data pipelines.")
            add_user_skill_safe(students["rohan@college.edu"], "Data Structures & Algorithms", "teach", "advanced", "Dynamic programming, trees, and graph algorithms.")
            add_user_skill_safe(students["rohan@college.edu"], "Python", "learn", "intermediate", "Refining idiomatic Python practices.")

            # Ananya: Teaches HTML5/CSS3 (Adv), React (Int); Learns Java (Beg)
            add_user_skill_safe(students["ananya@college.edu"], "HTML5 & CSS3", "teach", "advanced", "Modern responsive CSS, Flexbox, Grid, accessibility.")
            add_user_skill_safe(students["ananya@college.edu"], "React", "teach", "intermediate", "Hooks, state management, SPA design.")
            add_user_skill_safe(students["ananya@college.edu"], "Java", "learn", "beginner", "Preparing for campus placement interview rounds.")

            db.session.commit()

            # 4. Seed Exchange Requests & Sessions
            click.echo("[4/5] Seeding exchange agreements and learning sessions...")
            aarav = students["aarav@college.edu"]
            priya = students["priya@college.edu"]
            rohan = students["rohan@college.edu"]
            ananya = students["ananya@college.edu"]

            py_skill = skill_lookup["Python"]
            ui_skill = skill_lookup["UI/UX Design with Figma"]
            ml_skill = skill_lookup["Machine Learning"]
            html_skill = skill_lookup["HTML5 & CSS3"]
            sql_skill = skill_lookup["SQL & Relational Databases"]
            dsa_skill = skill_lookup["Data Structures & Algorithms"]

            # Agreement 1: Aarav <-> Priya (Accepted & Completed Session with Ratings)
            req1 = ExchangeRequest.query.filter_by(sender_id=aarav.id, receiver_id=priya.id, offered_skill_id=py_skill.id, requested_skill_id=ui_skill.id).first()
            if not req1:
                req1 = ExchangeRequest(
                    sender_id=aarav.id,
                    receiver_id=priya.id,
                    offered_skill_id=py_skill.id,
                    requested_skill_id=ui_skill.id,
                    message="Hi Priya! I'd love to learn Figma prototyping from you in exchange for Python tutoring.",
                    status='accepted'
                )
                db.session.add(req1)
                db.session.flush()

            sess1 = ExchangeSession.query.filter_by(request_id=req1.id).first()
            if not sess1:
                sess1 = ExchangeSession(
                    request_id=req1.id,
                    scheduled_at=datetime.now(timezone.utc) - timedelta(days=2),
                    duration_minutes=60,
                    mode="online",
                    meeting_details="https://meet.google.com/skillconnect-demo",
                    notes="Module 1: Figma auto-layout and Python data types walkthrough.",
                    status="completed"
                )
                db.session.add(sess1)
                db.session.flush()

            # Agreement 2: Rohan <-> Aarav (Accepted & Scheduled Upcoming Session)
            req2 = ExchangeRequest.query.filter_by(sender_id=rohan.id, receiver_id=aarav.id, offered_skill_id=ml_skill.id, requested_skill_id=py_skill.id).first()
            if not req2:
                req2 = ExchangeRequest(
                    sender_id=rohan.id,
                    receiver_id=aarav.id,
                    offered_skill_id=ml_skill.id,
                    requested_skill_id=py_skill.id,
                    message="Hey Aarav! Let's do an exchange session on Machine Learning foundations and Python scripting.",
                    status='accepted'
                )
                db.session.add(req2)
                db.session.flush()

            sess2 = ExchangeSession.query.filter_by(request_id=req2.id).first()
            if not sess2:
                sess2 = ExchangeSession(
                    request_id=req2.id,
                    scheduled_at=datetime.now(timezone.utc) + timedelta(days=1, hours=3),
                    duration_minutes=90,
                    mode="online",
                    meeting_details="https://meet.google.com/ml-py-collab",
                    notes="Linear regression in scikit-learn & Python virtual environments.",
                    status="scheduled"
                )
                db.session.add(sess2)
                db.session.flush()

            # Agreement 3: Ananya -> Aarav (Pending incoming request for Aarav)
            req3 = ExchangeRequest.query.filter_by(sender_id=ananya.id, receiver_id=aarav.id, offered_skill_id=html_skill.id, requested_skill_id=py_skill.id).first()
            if not req3:
                req3 = ExchangeRequest(
                    sender_id=ananya.id,
                    receiver_id=aarav.id,
                    offered_skill_id=html_skill.id,
                    requested_skill_id=py_skill.id,
                    message="Hi Aarav! Would you be open to exchanging Python backend lessons for modern CSS grid styling?",
                    status='pending'
                )
                db.session.add(req3)
                db.session.flush()

            # Agreement 4: Aarav -> Rohan (Pending outgoing request from Aarav)
            req4 = ExchangeRequest.query.filter_by(sender_id=aarav.id, receiver_id=rohan.id, offered_skill_id=sql_skill.id, requested_skill_id=dsa_skill.id).first()
            if not req4:
                req4 = ExchangeRequest(
                    sender_id=aarav.id,
                    receiver_id=rohan.id,
                    offered_skill_id=sql_skill.id,
                    requested_skill_id=dsa_skill.id,
                    message="Hey Rohan! I can share practical SQL optimization tips if you can mentor me in Graph traversal.",
                    status='pending'
                )
                db.session.add(req4)
                db.session.flush()

            # Agreement 5: Cancelled Request (Ananya -> Rohan)
            req5 = ExchangeRequest.query.filter_by(sender_id=ananya.id, receiver_id=rohan.id, offered_skill_id=html_skill.id, requested_skill_id=dsa_skill.id).first()
            if not req5:
                req5 = ExchangeRequest(
                    sender_id=ananya.id,
                    receiver_id=rohan.id,
                    offered_skill_id=html_skill.id,
                    requested_skill_id=dsa_skill.id,
                    message="Exchange request",
                    status='cancelled'
                )
                db.session.add(req5)
                db.session.flush()

            db.session.commit()

            # 5. Seed Post-Session Ratings on Completed Session
            click.echo("[5/5] Seeding post-session peer ratings...")
            # Aarav rates Priya 5 stars
            r_aarav = Rating.query.filter_by(session_id=sess1.id, reviewer_id=aarav.id).first()
            if not r_aarav:
                r_aarav = Rating(
                    session_id=sess1.id,
                    reviewer_id=aarav.id,
                    reviewee_id=priya.id,
                    score=5,
                    feedback="Priya explained design systems and wireframing in Figma with incredible patience and clarity!"
                )
                db.session.add(r_aarav)

            # Priya rates Aarav 5 stars
            r_priya = Rating.query.filter_by(session_id=sess1.id, reviewer_id=priya.id).first()
            if not r_priya:
                r_priya = Rating(
                    session_id=sess1.id,
                    reviewer_id=priya.id,
                    reviewee_id=aarav.id,
                    score=5,
                    feedback="Aarav walked through Python OOP concepts and practical backend patterns very thoroughly. Outstanding session!"
                )
                db.session.add(r_priya)

            db.session.commit()

            click.echo("\n========================================================")
            click.echo("[SUCCESS] Demonstration database seeded successfully!")
            click.echo("========================================================")
            click.echo("Demo Accounts (Password: Student@123):")
            click.echo("  - Aarav Sharma (CS):        aarav@college.edu")
            click.echo("  - Priya Patel (Design):     priya@college.edu")
            click.echo("  - Rohan Gupta (ML & DSA):   rohan@college.edu")
            click.echo("  - Ananya Iyer (Web Dev):    ananya@college.edu")
            click.echo("Administrator Account (Password: Admin@123):")
            click.echo("  - Prof. Sharma (Admin):     admin@college.edu")
            click.echo("========================================================")


