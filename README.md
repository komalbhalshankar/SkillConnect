# SkillConnect — Student Skill Exchange Platform

SkillConnect is a web-based peer-to-peer student skill exchange platform built with Python and Flask. The platform enables students to teach skills they possess and learn new skills from their peers through structured, reciprocal skill exchanges, scheduled learning sessions, transparent peer evaluations, and live dashboard analytics.

---

## 1. Core Modules

1. **User Authentication and Profile (Phase 2):** Student & Administrator registration, secure password hashing, session management, and academic profile configuration.
2. **Skill Management (Phase 3):** Categorized skill taxonomy, separate Teach/Learn portfolios, proficiency ratings, custom unlisted skill addition with duplicate avoidance, and strict ownership validation.
3. **Skill Discovery and Matching (Phase 3):** Database-backed student search and filtering, deterministic rule-based reciprocal compatibility engine (40/40/10/10 formula), transparent score explanations, and profile inspection.
4. **Skill Exchange and Session Management (Phase 4):** Proposal initiation, reciprocal skill validation, request state machine (`pending`, `accepted`, `rejected`, `cancelled`), learning session scheduling, and in-place session rescheduling.
5. **Rating, Feedback and Dashboard (Phase 5):** Post-session evaluations, peer reputation star ratings (1–5 stars), qualitative written feedback, personalized student dashboard, and responsive Chart.js visual activity distributions.

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
│   ├── forms/                  # WTForms definitions (auth, skills, exchange, review)
│   ├── models/                 # SQLAlchemy relational data models (User, Skill, UserSkill, ExchangeRequest, ExchangeSession, Rating)
│   ├── routes/                 # Blueprint controllers (auth, main, skills, matching, exchanges, admin)
│   ├── services/               # Service layer business logic (AuthService, SkillService, MatchingService, ExchangeService, RatingService, StatsService)
│   ├── static/                 # CSS stylesheets, JavaScript files
│   └── templates/              # Jinja2 presentation templates
│       ├── auth/               # Login & registration views
│       ├── main/               # Landing, dashboard, profile views
│       ├── skills/             # Skill portfolio management views
│       ├── matching/           # Student discovery & match recommendations
│       ├── exchanges/          # Exchange requests, scheduling, session detail, rating views
│       └── errors/             # Custom 403, 404, 500 error pages
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
│   ├── conftest.py             # Fixtures and test client
│   ├── test_auth.py            # Authentication, hashing, access control tests (10 tests)
│   ├── test_database.py        # Model constraints and CLI tests (4 tests)
│   ├── test_profile.py         # Profile update and ownership tests (4 tests)
│   ├── test_skills.py          # Skill CRUD, custom skills, ownership tests (19 tests)
│   ├── test_matching.py        # Rule-based matching engine & discovery tests (12 tests)
│   ├── test_exchanges.py       # Exchange requests, sessions, state machine tests (23 tests)
│   └── test_ratings.py         # Ratings, feedback, dashboard & charts tests (17 tests)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── run.py                      # Flask entry point and CLI commands
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
   python run.py init-db
   ```
   *Note: This creates all tables in `instance/skillconnect.db` without deleting or resetting any existing data.*

5. **Seed Standard Academic Skills & Categories (Idempotent):**
   ```bash
   python run.py seed-skills
   ```
   *Seeds standard curriculum categories (Programming, Database, Web Development, Design, Communication, Other) and standard baseline skills.*

6. **Create an Initial Administrator (CLI):**
   ```bash
   python run.py create-admin
   ```
   *Follow the interactive prompt to set admin name, email, and password securely.*

7. **Run the Application:**
   ```bash
   python run.py
   ```
   Open your browser and navigate to: [http://127.0.0.1:5000](http://127.0.0.1:5000)

*(Note: You can also use `flask --app run.py <command>` or `python -m flask --app run.py <command>`).*

---

## 5. Running Automated Tests

All functionality across Phases 1, 2, 3, 4, and 5 is covered by automated unit and integration tests using `pytest` and Flask's test client running against an isolated in-memory SQLite database (`sqlite:///:memory:`):

```bash
python -m pytest -v
```

### Verified Test Suite (89/89 Passing — 100% Pass Rate):
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
- **Skill Management (`tests/test_skills.py` — 19 tests):**
  - Adding skills to Teach and Learn portfolios with proficiency and notes.
  - Associating same skill in both Teach and Learn lists.
  - Preventing duplicate skill addition under the same skill type.
  - Adding custom unlisted skills with category assignment.
  - Deduplicating custom skills case-insensitively.
  - Updating skill type, proficiency, and notes.
  - Deleting skills from portfolio.
  - Cross-user ownership protection (HTTP 403 Forbidden on unauthorized edit/delete).
  - Admin category and skill creation via portal.
  - Student RBAC restrictions on admin skill routes (HTTP 403 Forbidden).
  - CLI skill seeding command (`flask seed-skills`).
  - Public skill catalog browser (`/skills/explore`).
- **Skill Discovery & Matching (`tests/test_matching.py` — 12 tests):**
  - Full reciprocal matching score (100% score calculation with forward and reverse breakdowns).
  - One-way matching score (directional calculation).
  - Disjoint skills return zero match (omitted from recommendations).
  - Self-matching prevention (current user excluded from recommendations and discovery).
  - Score bounds strictly verified within $[0, 100]$.
  - Deterministic ranking: reciprocal matches first, score descending, matched skills count descending, candidate ID ascending.
  - Discovery student search by skill name.
  - Discovery filtering by academic category and proficiency level.
  - Handling empty search results gracefully with helpful user prompts.
  - Matching recommendations page rendering with score cards, badges, and breakdown lists.
  - Student profile inspection (`/matching/student/<id>`) displaying peer profile and active proposal button.
  - Route protection redirecting unauthenticated visitors to login.
- **Skill Exchange & Session Management (`tests/test_exchanges.py` — 23 tests):**
  - Valid proposal creation, pending status, correct skill associations.
  - Rejection of self-proposals (`sender_id != receiver_id`).
  - Rejection of offered skills not listed in sender's TEACH portfolio.
  - Rejection of requested skills not listed in receiver's TEACH portfolio.
  - Rejection of requested skills not listed in sender's LEARN wishlist.
  - Duplicate active pending request prevention.
  - Filtering incoming and outgoing requests for participating students.
  - Proposal acceptance and decline transitions (`accepted`, `rejected`).
  - Outgoing proposal cancellation by sender (`cancelled`).
  - Prevention of invalid request transitions on finalized requests.
  - Strict participant authorization checks on accept/reject/cancel operations.
  - Anti-IDOR protection blocking non-participants from viewing exchange proposals (HTTP 404).
  - Session scheduling after request acceptance.
  - Blocking session scheduling for pending or rejected requests.
  - Validation blocking scheduling sessions in the past.
  - Authorized participant session detail access and non-participant blocking.
  - Session completion and cancellation lifecycle.
  - Prevention of invalid session state transitions.
  - Documented in-place rescheduling policy for cancelled sessions.
  - Clean separation of sessions into upcoming and past history.
  - Route-level authentication enforcement.
- **Rating, Feedback & Dashboard (`tests/test_ratings.py` — 17 tests):**
  - Valid rating submission after completion (1–5 stars and feedback comments).
  - Rejection of ratings before completion (e.g. Scheduled session).
  - Rejection of ratings for cancelled sessions.
  - Rejection of invalid rating scores (outside bounds 1–5 or non-integer).
  - Prevention of self-rating.
  - Prevention of ratings by unrelated third-party students.
  - Prevention of duplicate ratings by same reviewer for same session.
  - Independent bilateral ratings from both participants.
  - Accurate arithmetic average rating and 1-decimal rounding.
  - Review count and star distribution calculation.
  - Validation of max 500 characters for written feedback.
  - Safe handling of missing or invalid session IDs.
  - Personalized dashboard statistics reflecting actual database records.
  - Graceful handling of brand new students with zero activity (safe defaults and zero counts).
  - Prevention of cross-user data leakage.
  - Full HTTP GET/POST workflow for rating submission.
  - Dashboard route view and Chart.js payload serialization.
  - Profile and peer inspection views displaying received reviews and star ratings.

---

## 6. Implementation Progress

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Phase 1** | Requirements, UML Use Case, Architecture & Skeleton | **Completed** |
| **Phase 2** | Database Foundation, Authentication & Student Profile | **Completed & Verified** (18/18 Tests Passed) |
| **Phase 3** | Skill Management (Module 2) & Skill Discovery and Matching (Module 3) | **Completed & Verified** (49/49 Tests Passed) |
| **Phase 4** | Skill Exchange and Session Management (Module 4) | **Completed & Verified** (72/72 Tests Passed) |
| **Phase 5** | Rating, Feedback and Dashboard (Module 5) | **Completed & Verified** (89/89 Tests Passed) |
