# SkillConnect — Student Skill Exchange Platform

SkillConnect is a web-based peer-to-peer student skill exchange platform built with Python and Flask. The platform enables students to teach skills they possess and learn new skills from their peers through structured, reciprocal skill exchanges, scheduled learning sessions, and transparent evaluations.

---

## 1. Core Modules

1. **User Authentication and Profile:** Student & Administrator registration, secure password hashing, session management, and academic profile configuration.
2. **Skill Management:** Categorized skill taxonomy, Teach/Learn portfolios, proficiency ratings, and ownership validation.
3. **Skill Discovery and Matching:** Deterministic, rule-based two-way compatibility matching engine with scoring breakdown.
4. **Skill Exchange and Session Management:** Proposal negotiation, state machine transitions, and session scheduling.
5. **Rating, Feedback and Dashboard:** Post-session reviews, peer reputation ratings, and Chart.js analytics dashboards.

---

## 2. Technology Stack

- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JavaScript, Chart.js
- **Testing:** pytest, Flask test client
- **Version Control:** Git, GitHub

---

## 3. Project Structure

```
Python_Mini_Project_Sem l/
├── app/                        # Application package
│   ├── __init__.py             # Application factory (create_app)
│   ├── config.py               # Development, testing, and production configs
│   ├── extensions.py           # Database, LoginManager, CSRF extensions
│   ├── forms/                  # WTForms definitions
│   ├── models/                 # SQLAlchemy relational data models
│   ├── routes/                 # Blueprint controllers (auth, main, skills, matching, exchanges, admin)
│   ├── services/               # Service layer business logic
│   ├── static/                 # CSS stylesheets, JavaScript files
│   └── templates/              # Jinja2 presentation templates
├── docs/                       # Project documentation & diagrams
│   ├── requirements.md         # System requirements specification (SRS)
│   ├── use_case_diagram.md     # UML use case diagram documentation
│   ├── use_case_diagram.svg    # Rendered vector UML use case diagram
│   ├── use_case_diagram.mmd    # Mermaid diagram source
│   ├── use_case_diagram.puml   # PlantUML diagram source
│   ├── architecture.md         # System architecture specification
│   ├── database_design.md      # Relational schema design and data dictionary
│   ├── matching_algorithm.md   # Mathematical specification of the matching engine
│   └── test_plan.md            # Comprehensive QA test plan
├── tests/                      # Automated test suites (pytest)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── run.py                      # Flask entry point
```

---

## 4. Setup & Installation

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Git

### Quickstart

1. **Activate virtual environment:**
   ```bash
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   # Create .env from template if not present
   copy .env.example .env
   ```

4. **Initialize SQLite Database (Safe, non-destructive):**
   ```bash
   flask --app run.py init-db
   ```
   *Note: This creates all tables in `instance/skillconnect.db` without deleting or resetting any existing data.*

5. **Seed Standard Academic Skills & Categories (Idempotent):**
   ```bash
   flask --app run.py seed-skills
   ```
   *Seeds standard curriculum categories (Programming, Web Dev, Data Science, CS Core, Design, Communication) and 24+ baseline skills.*

6. **Create an Initial Administrator (CLI):**
   ```bash
   flask --app run.py create-admin
   ```
   *Follow the interactive prompt to set admin name, email, and password securely.*

7. **Run the Application:**
   ```bash
   python run.py
   ```
   Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 5. Running Automated Tests

All functionality across Phase 2 and Phase 3 is covered by automated unit and integration tests using `pytest` and Flask's test client running against an isolated in-memory SQLite database (`sqlite:///:memory:`):

```bash
pytest -v
```

### Verified Test Suite (33/33 Passing):
- **Authentication & RBAC (`tests/test_auth.py` — 10 tests):**
  - Registration, duplicate email rejection, Werkzeug password hashing.
  - Successful login, failed login (bad password / unknown email), logout.
  - Route protection (redirection to login) and Role-Based Access Control (`/admin` forbidden for students, allowed for admins).
- **Profile Management (`tests/test_profile.py` — 4 tests):**
  - Profile viewing, profile updating (name, college, bio, availability).
  - Validation enforcement (empty name rejection) and ownership isolation.
- **Database & Models (`tests/test_database.py` — 4 tests):**
  - Unique email database constraints.
  - `SkillCategory` and `Skill` model relationships.
  - Safe database initialization CLI (`flask init-db`) and administrator creation CLI (`flask create-admin`).
- **Skill Taxonomy & Portfolios (`tests/test_skills.py` — 15 tests):**
  - Adding skills to Teach and Learn portfolios with proficiency and notes.
  - Mutual exclusivity enforcement (cannot add same skill to both Teach and Learn).
  - Duplicate prevention in the same skill list.
  - Updating proficiency and notes.
  - Deleting skills from portfolio.
  - Cross-user ownership protection (HTTP 403 Forbidden on unauthorized edit/delete).
  - Admin category and skill creation via portal.
  - Student RBAC restrictions on admin skill routes (HTTP 403 Forbidden).
  - CLI skill seeding command (`flask seed-skills`).
  - Public skill catalog browser (`/skills/explore`).

---

## 6. Implementation Progress

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Phase 1** | Requirements, UML Use Case, Architecture & Skeleton | **Completed** |
| **Phase 2** | Database Foundation, Authentication & Student Profile | **Completed & Verified** |
| **Phase 3** | Skill Taxonomy, Categories & Student Skill Portfolios | **Completed & Verified** |
| **Phase 4** | Two-Way Reciprocal Matching Engine & Compatibility Scoring | *Next Milestone (Pending Approval)* |
| **Phase 5** | Exchange Requests, Sessions, Feedback & Analytics | *Planned* |


