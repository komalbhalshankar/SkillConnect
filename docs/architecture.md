# SkillConnect — Architecture Specification
**Version:** 1.0  
**Project:** SkillConnect — Student Skill Exchange Platform  
**Architecture Pattern:** Layered MVC with Flask Application Factory, Blueprint Modularization & Service Layer

---

## 1. Architectural Philosophy
SkillConnect is engineered to be **production-structured, maintainable, extensible, and clean**, avoiding the monolithic single-file pitfall typical of student projects. It strictly separates concerns:

1. **Presentation Layer:** Jinja2 templates styled with Bootstrap 5, interactive Vanilla JavaScript, and Chart.js for data visualization.
2. **Controller / Routing Layer (Blueprints):** Thin Flask route handlers responsible for HTTP request handling, session authentication checks, input collection, and response dispatching.
3. **Service Layer (Domain Logic):** Dedicated business logic classes encapsulating matching logic, request state machines, session management, and rating computations.
4. **Data Access / Persistence Layer:** SQLAlchemy ORM models with SQLite storage, declarative relationships, foreign keys, and cascading constraints.

```mermaid
graph TD
    User["Web Browser Client"] -->|HTTP / HTTPS| FlaskApp["Flask WSGI Application"]
    
    subgraph Controller_Tier ["Blueprints (Routing Layer)"]
        AuthBP["auth_bp (/auth)"]
        MainBP["main_bp (/)"]
        SkillBP["skills_bp (/skills)"]
        MatchBP["matching_bp (/matching)"]
        ExchBP["exchanges_bp (/exchanges)"]
        SessBP["sessions_bp (/sessions)"]
        AdminBP["admin_bp (/admin)"]
    end
    
    FlaskApp --> Controller_Tier
    
    subgraph Service_Tier ["Service Layer (Business Logic)"]
        AuthService["AuthService"]
        SkillService["SkillService"]
        MatchingEngine["MatchingEngine"]
        ExchangeService["ExchangeService"]
        RatingService["RatingService"]
        StatsService["StatsService"]
    end
    
    Controller_Tier --> Service_Tier
    
    subgraph Persistence_Tier ["Data Layer (SQLAlchemy ORM)"]
        Models["User, SkillCategory, Skill, UserSkill, ExchangeRequest, ExchangeSession, Rating"]
        SQLiteDB[("SQLite Database<br/>instance/skillconnect.db")]
    end
    
    Service_Tier --> Models
    Models --> SQLiteDB
```

---

## 2. Directory Structure
```
Python_Mini_Project_Sem l/
│
├── app/                            # Application package root
│   ├── __init__.py                 # Application factory (create_app)
│   ├── config.py                   # Centralized configuration (Development, Testing, Production)
│   ├── extensions.py               # Instantiated Flask extensions (db, login_manager, csrf)
│   │
│   ├── models/                     # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py                 # User model (Student & Admin)
│   │   ├── skill.py                # SkillCategory, Skill, UserSkill models
│   │   ├── exchange.py             # ExchangeRequest, ExchangeSession models
│   │   └── rating.py               # Rating & feedback model
│   │
│   ├── services/                   # Service Layer (Business Logic)
│   │   ├── __init__.py
│   │   ├── auth_service.py         # Registration, credential verification, profile updates
│   │   ├── skill_service.py        # Skill catalog & user skill portfolio management
│   │   ├── matching_service.py     # Deterministic two-way matching engine
│   │   ├── exchange_service.py     # Exchange requests & session lifecycle state machine
│   │   └── stats_service.py        # Dashboard analytics & platform reporting
│   │
│   ├── forms/                      # WTForms form validations & CSRF definitions
│   │   ├── __init__.py
│   │   ├── auth_forms.py
│   │   ├── skill_forms.py
│   │   ├── exchange_forms.py
│   │   └── admin_forms.py
│   │
│   ├── routes/                     # Blueprint Route Controllers
│   │   ├── __init__.py
│   │   ├── auth.py                 # Authentication routes (/auth/login, /auth/register)
│   │   ├── main.py                 # Home, dashboard, public directory, profile
│   │   ├── skills.py               # Skill portfolio CRUD
│   │   ├── matching.py             # Match recommendations & compatibility breakdown
│   │   ├── exchanges.py            # Proposals & session scheduling
│   │   └── admin.py                # Platform administration & stats
│   │
│   ├── static/                     # Static Web Assets
│   │   ├── css/
│   │   │   └── custom.css          # Custom aesthetic stylesheet & styling tokens
│   │   └── js/
│   │       ├── main.js             # General interactive client scripting
│   │       └── dashboard-charts.js # Chart.js visualizations
│   │
│   └── templates/                  # Jinja2 HTML Templates
│       ├── base.html               # Master layout with responsive navbar & footer
│       ├── auth/                   # Login, register templates
│       ├── main/                   # Index landing, dashboard, directory, profile
│       ├── skills/                 # Manage skills, add/edit modals
│       ├── matching/               # Matching recommendations & breakdown
│       ├── exchanges/              # Requests list, session scheduling, detail view
│       ├── reviews/                # Session completion & rating submission modal/page
│       ├── admin/                  # Admin dashboard & category management
│       └── errors/                 # 404, 403, 500 error pages
│
├── docs/                           # Documentation
│   ├── requirements.md
│   ├── use_case_diagram.md
│   ├── use_case_diagram.svg
│   ├── use_case_diagram.puml
│   ├── use_case_diagram.mmd
│   ├── architecture.md
│   ├── database_design.md
│   ├── matching_algorithm.md
│   └── test_plan.md
│
├── tests/                          # Automated Pytest Suite
│   ├── conftest.py                 # Pytest fixtures, test database, test clients
│   ├── test_auth.py                # Authentication, hashing, access control tests
│   ├── test_skills.py              # Skill CRUD, ownership enforcement tests
│   ├── test_matching.py            # Matching algorithm unit & edge case tests
│   ├── test_exchanges.py           # Exchange & session state machine tests
│   ├── test_ratings.py             # Rating validation & duplicate prevention tests
│   └── test_admin.py               # Admin role authorization & stats tests
│
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore patterns
├── README.md                       # Comprehensive setup and user guide
├── requirements.txt                # Pinned dependency requirements
└── run.py                          # Application entry point & CLI commands (seed, init-db)
```

---

## 3. Application Lifecycle & Startup
- The application is instantiated via `create_app(config_name=None)` defined in `app/__init__.py`.
- Flask extensions (`SQLAlchemy`, `LoginManager`, `CSRFProtect`) are decoupled from the application instance and initialized via `init_app(app)`.
- Blueprints are registered with distinct URL prefixes (`/auth`, `/skills`, `/matching`, `/exchanges`, `/admin`).
- Database initialization and seeding are exposed as safe CLI commands (`flask init-db`, `flask seed-data`), ensuring existing user data is never wiped automatically on server start.

---

## 4. Extensibility & Future Readiness
The modular architecture guarantees that future modules (e.g., Real-time Chat, Video Call WebRTC integration, In-App Notifications, Badge / Gamification system) can be added cleanly as new blueprints and models without refactoring the foundational modules.

---

## 5. Implementation Phases & Architecture Status

### Phase 2: Database Foundation, Authentication & Student Profile (Completed)
- **Application Factory:** `create_app()` dynamically loads configuration (`DevelopmentConfig`, `TestingConfig`, `ProductionConfig`) and binds extensions (`db`, `login_manager`, `csrf`).
- **Active Blueprints:**
  - `main_bp` (`/`): Landing page, placeholder student dashboard, and profile management.
  - `auth_bp` (`/auth`): Student registration, session login, and logout.
  - `admin_bp` (`/admin`): Role-restricted administration portal.
- **ORM Persistence:**
  - `User`: Primary authentication entity with password hashing (Werkzeug), college, bio, availability, and role-based permissions (`student`, `admin`).
  - `SkillCategory` & `Skill`: Foundation taxonomy models establishing foreign key relationships for future skill portfolio association.
  - Forward-compatible relational hooks for `UserSkill`, `ExchangeRequest`, `ExchangeSession`, and `Rating`.
- **Administrative CLI Tooling:**
  - `flask init-db`: Non-destructive table initialization.
  - `flask create-admin`: Secure administrator provisioning without hardcoded credentials.

### Phase 3: Skill Management, Discovery & Matching (Completed & Verified)
- **Active Blueprints & Controllers:**
  - `skills_bp` (`/skills`):
    - `GET /skills/`: Personal skill portfolio view displaying separate Teach and Learn lists with proficiency badges and notes.
    - `POST /skills/add`: Add skill to Teach or Learn portfolio. Supports selecting existing skills or adding custom unlisted skills with automatic category assignment and duplicate avoidance.
    - `POST /skills/edit/<int:user_skill_id>`: Edit skill type, proficiency, and notes with strict ownership validation.
    - `POST /skills/delete/<int:user_skill_id>`: Remove skill from portfolio with strict ownership validation.
    - `GET /skills/explore`: Public/student categorized skill catalog browser.
  - `matching_bp` (`/matching`):
    - `GET /matching/`: Matching recommendations view with transparent compatibility scores (0–100%), directional matched skill breakdowns, and score justifications. Supports reciprocal filter toggle (`?reciprocal=1`).
    - `GET /matching/discover`: Student directory with live database-backed search by skill name and filters for category, proficiency, and intent (`teach`, `learn`, or `all`).
    - `GET /matching/student/<int:user_id>`: Student profile inspection view showing peer bio, college, availability, skills offered/desired, and bilateral compatibility overview.
  - `admin_bp` (`/admin`):
    - `POST /admin/categories/add`: Admin category creation.
    - `POST /admin/skills/add`: Admin standardized skill creation under a category.
- **Domain Service Layer:**
  - `SkillService`:
    - Handles addition of standard or custom unlisted skills (reusing existing skills case-insensitively).
    - Permits a student to associate the same skill in both Teach and Learn (e.g. basic instructor vs advanced learner), while preventing duplicate entries under the same `skill_type`.
    - Enforces ownership checks on mutations.
    - Implements database-backed student search and filtering excluding the current user.
  - `MatchingService`:
    - Implements deterministic rule-based matching formula: 40 pts (forward match) + 40 pts (reverse match) + 10 pts (category bonus) + 10 pts (proficiency bonus).
    - Strictly bounds scores between 0% and 100%.
    - Provides deterministic ranking: reciprocal first, score descending, matched skills count descending, candidate ID ascending.
    - Excludes students with zero complementary skills.
- **CLI Seeding:**
  - `flask seed-skills`: Idempotently seeds standard academic categories (Programming, Database, Web Development, Design, Communication, Other) and standard skill sets.

### Phase 4: Skill Exchange & Session Management (Completed & Verified)
- **Active Blueprints & Controllers:**
  - `exchanges_bp` (`/exchanges`):
    - `GET /exchanges/`: Exchange requests hub displaying incoming and outgoing proposals with status badges and filter tabs.
    - `GET /exchanges/<int:request_id>`: Detailed view of an exchange proposal, participants, agreed skills, status timeline, and linked session.
    - `GET, POST /exchanges/new`: Create and send skill exchange proposal with pre-populated matched skills.
    - `POST /exchanges/respond/<int:request_id>/<action>`: Receiver accepts or rejects an incoming pending request.
    - `POST /exchanges/cancel/<int:request_id>`: Sender cancels an outgoing pending request.
    - `GET, POST /exchanges/schedule/<int:request_id>`: Schedule or reschedule learning session for an accepted exchange agreement.
    - `GET /exchanges/sessions`: Sessions directory listing upcoming scheduled meetings and past/historical sessions.
    - `GET /exchanges/sessions/<int:session_id>`: Detailed session view with meeting mode, link/room location, and agenda notes.
    - `POST /exchanges/sessions/<int:session_id>/complete`: Participant marks a scheduled session as completed.
    - `POST /exchanges/sessions/<int:session_id>/cancel`: Participant cancels a scheduled session.
- **Domain Service Layer (`ExchangeService`):**
  - **Proposal Validation:**
    - Rejects self-proposals (`sender_id != receiver_id`).
    - Validates that offered skill is in sender's TEACH portfolio.
    - Validates that requested skill is in sender's LEARN portfolio and receiver's TEACH portfolio.
    - Validates reciprocal alignment with receiver's wishlist.
    - Enforces duplicate prevention against active pending or accepted agreements.
  - **State Machine Transitions:**
    - Request: `pending` $\to$ `accepted` | `rejected` | `cancelled`.
    - Session: `scheduled` $\to$ `completed` | `cancelled`.
    - Rescheduling Policy: Cancelled sessions can be rescheduled by participants, updating meeting logistics and resetting status to `scheduled`.
  - **Authorization & Anti-IDOR:**
    - Strict participant validation ensures only authorized students can view, respond, cancel, or modify requests and sessions.
- **Verification:** 72 total unit and integration tests passing across all active modules.




