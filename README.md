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
│   ├── test_ratings.py         # Ratings, feedback, dashboard & charts tests (17 tests)
│   └── test_e2e_flow.py        # End-to-end integration workflows for students & admin (2 tests)
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
└── run.py                      # Flask entry point and CLI commands
```

---

## 4. Visual Studio Code Quick Start Guide

Follow these verified steps to run the complete SkillConnect application locally with zero prior configuration:

### Prerequisites
- **Python:** Version 3.10 to 3.14 (tested and verified on Python 3.14.7)
- **Editor:** Visual Studio Code (recommended: [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python))
- **Terminal:** Windows PowerShell or bash/zsh on Linux/macOS

### 10-Step Setup Workflow

1. **Open Project in VS Code:**
   Open the cloned folder in VS Code (`File > Open Folder...`).

2. **Open Terminal:**
   Press `` Ctrl + ` `` to open an integrated terminal.

3. **Create Python Virtual Environment:**
   ```powershell
   # Windows PowerShell:
   python -m venv .venv
   ```
   *(On Linux/macOS: `python3 -m venv .venv`)*

4. **Activate the Virtual Environment:**
   ```powershell
   # Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   ```
   *(If PowerShell displays an execution policy restriction, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and re-run the activation script)*  
   *(On Linux/macOS: `source .venv/bin/activate`)*

5. **Install Project Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

6. **Configure Environment File:**
   ```powershell
   # Windows PowerShell:
   Copy-Item .env.example .env
   ```
   *(On Linux/macOS: `cp .env.example .env`)*

7. **Initialize SQLite Database (Safe & Non-Destructive):**
   ```powershell
   python run.py init-db
   ```
   *Creates schema tables in `instance/skillconnect.db` safely without wiping or corrupting existing data.*

8. **Seed Demonstration Data (Idempotent):**
   ```powershell
   python run.py seed-demo
   ```
   *Populates academic taxonomy, complementary student profiles, reciprocal and one-way matches, active/accepted proposals, scheduled/completed sessions, and bilateral review ratings.*

9. **Start Local Flask Development Server:**
   ```powershell
   python run.py
   ```

10. **Open in Browser:**
    Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000)

*To stop the local server at any time, press `Ctrl + C` in the terminal.*

---

## 5. Demonstration Accounts & Login Credentials

When using `python run.py seed-demo`, the platform is instantly provisioned with realistic, interconnected student peers and an administrator:

| Role | Account Name | Email | Password | Primary Skills & Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Admin** | Prof. Sharma (Admin) | `admin@college.edu` | `Admin@123` | Platform governance, Category & Standard Skill creation |
| **Student** | Aarav Sharma | `aarav@college.edu` | `Student@123` | **Teaches:** Python, Data Structures <br>**Learns:** UI/UX Design, Docker <br>*100% Reciprocal Match with Priya* |
| **Student** | Priya Patel | `priya@college.edu` | `Student@123` | **Teaches:** UI/UX Design, Web Development <br>**Learns:** Python, Cloud Computing <br>*Has completed session & 5-star rating with Aarav* |
| **Student** | Rohan Gupta | `rohan@college.edu` | `Student@123` | **Teaches:** SQL & Database Design, Machine Learning <br>**Learns:** Python, Data Structures <br>*One-way match with Aarav; accepted/scheduled proposal* |
| **Student** | Ananya Iyer | `ananya@college.edu` | `Student@123` | **Teaches:** HTML5 & CSS3 <br>**Learns:** Python, Data Structures <br>*Newer student profile with pending proposal for Aarav* |

> [!NOTE]
> Demo passwords use secure Argon2/Werkzeug hashes stored in SQLite. For production deployments, change secrets in `.env` and assign strong custom passwords.

---

## 6. End-to-End Workflow Testing Guide

To test the entire 5-module flow manually in 3 minutes:

1. **Student A Login:** Log in as `aarav@college.edu` (Password: `Student@123`).
2. **Review Dashboard:** Navigate to [Dashboard](http://127.0.0.1:5000/dashboard) to view live statistics and Chart.js skill distributions.
3. **Discover & Match:** Go to [Matches](http://127.0.0.1:5000/matching/) to see a 100% Reciprocal match card for Priya Patel with full score explanations.
4. **Propose Exchange:** Click **Send Exchange Request** to propose a skill exchange (e.g. Python for UI/UX Design).
5. **Student B Login:** Log out and log in as `priya@college.edu`. View the incoming proposal in [Exchange Proposals](http://127.0.0.1:5000/exchanges/?tab=incoming) and click **Accept**.
6. **Schedule Learning Session:** Click **Schedule Session**, pick an upcoming date/time, and provide meeting link details.
7. **Complete & Rate:** Mark the session as **Completed**, then click **Rate Partner** to submit star ratings (1–5) and written feedback.
8. **Verify Updated Profile & Dashboard:** View Aarav's updated average rating, review count, and dynamic Chart.js stats.
9. **Admin Governance:** Log in as `admin@college.edu` (Password: `Admin@123`), visit [Admin Portal](http://127.0.0.1:5000/admin), and create a new skill category.

---

## 7. Running Automated Test Suite

All 5 modules plus administrative governance and multi-user integration flows are verified using `pytest`:

```bash
python -m pytest -v
```

### Verified Test Suite Summary (91/91 Passing — 100% Pass Rate):

- **End-to-End Integration Flows (`tests/test_e2e_flow.py` — 2 tests):**
  - Multi-user student lifecycle: registration, profile completion, skill listing, discovery, 100% reciprocal matching, proposal creation, acceptance, session scheduling, completion, bilateral ratings, and dashboard verification.
  - Full admin governance: category/skill creation, standard taxonomy listing, and student permission rejection.
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

## 8. Common Troubleshooting & Quick Fixes

- **PowerShell Script Execution Error:**
  - *Symptom:* `Activate.ps1 cannot be loaded because running scripts is disabled on this system.`
  - *Fix:* Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell terminal, then re-run `.\.venv\Scripts\Activate.ps1`.
- **Port 5000 Already in Use:**
  - *Symptom:* `OSError: [Errno 98] Address already in use` or Windows equivalent.
  - *Fix:* Specify an alternative port: `flask --app run.py run --port 5001` or set `PORT=5001` in `.env`.
- **Missing `.env` File:**
  - *Symptom:* Warning that `.env` was not found.
  - *Fix:* Run `Copy-Item .env.example .env` (PowerShell) or `cp .env.example .env` (bash).

---

## 9. Limitations & Future Roadmap

### Honest Project Limitations
- **Rule-Based Matching:** Matching is governed by an explicit deterministic algorithm (40/40/10/10 formula) rather than probabilistic Machine Learning models.
- **Video Conferencing:** Meeting links (e.g. Google Meet, Zoom, Microsoft Teams) are coordinated via URLs rather than built-in WebRTC video streaming.
- **Single Institutional Scope:** Designed for college campus peer learning rather than multi-tenant enterprise deployment.

### Future Enhancements
- Automated calendar invite integration (.ics calendar attachments).
- Real-time in-app peer messaging and session chat notifications.
- Skill endorsement badges based on cumulative ratings threshold.

---

## 10. Implementation Progress

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Phase 1** | Requirements, UML Use Case, Architecture & Skeleton | **Completed** |
| **Phase 2** | Database Foundation, Authentication & Student Profile | **Completed & Verified** (18/18 Tests Passed) |
| **Phase 3** | Skill Management (Module 2) & Skill Discovery and Matching (Module 3) | **Completed & Verified** (49/49 Tests Passed) |
| **Phase 4** | Skill Exchange and Session Management (Module 4) | **Completed & Verified** (72/72 Tests Passed) |
| **Phase 5** | Rating, Feedback and Dashboard (Module 5) | **Completed & Verified** (89/89 Tests Passed) |
| **Phase 6** | Final Verification, E2E Integration, Demo Seeding & Release Readiness | **Completed & Verified** (91/91 Tests Passed) |
