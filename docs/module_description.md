# SkillConnect — System Module Architecture & Descriptions

**Project:** SkillConnect — Peer-to-Peer Student Skill Exchange Platform  
**Academic Program:** MCA Semester 1 Mini Project  
**Architecture:** Layered MVC with Flask Blueprints, Service Layer & SQLAlchemy 3NF Models  
**Test Suite:** 91 / 91 Verified Tests Passing (100%)  

---

## 1. Visual Specification (Image Assets)

- **High-Resolution Image (PNG):** [module_description.png](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/module_description.png) *(1760 &times; 1270 px)*
- **Lossless Vector Graphic (SVG):** [module_description.svg](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/module_description.svg) *(Infinite zoom with zero pixelation)*
- **Interactive Diagrams Hub:** [diagrams_viewer.html](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/diagrams_viewer.html)

![SkillConnect System Module Architecture](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/module_description.png)

---

## 2. System Modules Detailed Breakdown

### Module 01: User Authentication & Profile Management
- **Tier:** Identity & Access Tier
- **Routing Endpoints:** `/auth/register`, `/auth/login`, `/auth/logout`, `/profile`, `/profile/edit`
- **Controller Blueprint:** `app/routes/auth.py`, `app/routes/main.py`
- **Service Layer:** `AuthService` (`app/services/auth_service.py`)
- **Entities & Models:** `User` (`app/models/user.py`)
- **Core Capabilities:**
  - Secure student and administrator registration with institutional format validation.
  - Cryptographically salted password hashing (`pbkdf2:sha256`) via Werkzeug security.
  - Session state management via `Flask-Login` with `@login_required` route decorators.
  - Role-Based Access Control (RBAC) supporting `'student'` and `'admin'` privileges.
  - Editable user profiles including institution (`college`), biography (`bio`), and study hours (`availability`).
- **Test Verification:** 100% Passed (14 Unit & Integration Tests).

---

### Module 02: Skill Portfolio & Taxonomy Management
- **Tier:** Portfolio & Domain Tier
- **Routing Endpoints:** `/skills`, `/skills/add`, `/skills/<id>/edit`, `/skills/<id>/delete`
- **Controller Blueprint:** `app/routes/skills.py`
- **Service Layer:** `SkillService` (`app/services/skill_service.py`)
- **Entities & Models:** `SkillCategory`, `Skill`, `UserSkill` (`app/models/skill.py`)
- **Core Capabilities:**
  - 8 Standardized pre-seeded academic and technical taxonomy categories (Programming & Tech, Database, Web Development, Design, Communication, etc.).
  - Bilateral student intent categorization: `teach` (offering mentorship) vs. `learn` (seeking guidance).
  - 3-tier self-assessed proficiency scale: `Beginner`, `Intermediate`, `Advanced`.
  - Automatic case-insensitive skill deduplication when students register custom skills.
  - Composite unique constraint `UNIQUE(user_id, skill_id, skill_type)` preventing duplicate intent entries.
- **Test Verification:** 100% Passed (19 Unit & Integration Tests).

---

### Module 03: Peer Discovery & Two-Way Matching Engine
- **Tier:** Algorithm & Recommendation Tier
- **Routing Endpoints:** `/matching`, `/matching/directory`, `/matching/profile/<id>`
- **Controller Blueprint:** `app/routes/matching.py`
- **Service Layer:** `MatchingEngine` (`app/services/matching_service.py`)
- **Entities & Models:** Queries `User`, `UserSkill`, `Skill`
- **Core Capabilities:**
  - Global searchable peer student directory with live text queries and multi-attribute filters (category, proficiency, intent).
  - Deterministic 0–100% bilateral compatibility scoring engine:
    - 40% Weight: Direct Reciprocal Need Synergy ($A_{\text{learn}} \cap B_{\text{teach}}$).
    - 40% Weight: Direct Reciprocal Offer Synergy ($A_{\text{teach}} \cap B_{\text{learn}}$).
    - 10% Weight: Domain / Subject Category Affinity.
    - 10% Weight: Proficiency Level Alignment (mentor proficiency $\ge$ learner proficiency).
  - Transparent itemized compatibility breakdown explaining matched skills and bonus points.
  - Strict self-exclusion (`user_id != current_user.id`).
- **Test Verification:** 100% Passed (12 Unit & Integration Tests).

---

### Module 04: Skill Exchange & Session Lifecycle Management
- **Tier:** Workflow & Operations Tier
- **Routing Endpoints:** `/exchanges`, `/exchanges/create`, `/exchanges/<id>/accept`, `/exchanges/<id>/reject`, `/exchanges/<id>/cancel`, `/sessions/<id>/schedule`
- **Controller Blueprint:** `app/routes/exchanges.py`
- **Service Layer:** `ExchangeService` (`app/services/exchange_service.py`)
- **Entities & Models:** `ExchangeRequest`, `ExchangeSession` (`app/models/exchange.py`)
- **Core Capabilities:**
  - Bilateral exchange proposals linking offered teach skills and requested learn skills.
  - Rigid validation prohibiting self-proposals (`sender_id != receiver_id`).
  - 4-state proposal lifecycle state machine: `pending` $\rightarrow$ `accepted`, `rejected`, or `cancelled`.
  - 1-to-1 operational session booking generated upon request acceptance (`request_id` UNIQUE).
  - Meeting scheduling with date/time, default 60-minute duration, agenda notes, and delivery format (`online`, `in_person`, `hybrid`).
- **Test Verification:** 100% Passed (23 Unit & Integration Tests).

---

### Module 05: Peer Rating, Feedback & Analytics Dashboard
- **Tier:** Evaluation & Analytics Tier
- **Routing Endpoints:** `/dashboard`, `/sessions/<id>/rate`, `/reviews/<id>`
- **Controller Blueprint:** `app/routes/main.py`, `app/routes/exchanges.py`
- **Service Layer:** `RatingService` (`app/services/rating_service.py`), `StatsService` (`app/services/stats_service.py`)
- **Entities & Models:** `Rating` (`app/models/rating.py`), `ExchangeSession`, `User`
- **Core Capabilities:**
  - Bilateral post-session evaluations with 1-to-5 star ratings bound by database `CHECK(score BETWEEN 1 AND 5)`.
  - Qualitative written feedback, remarks, and peer testimonials.
  - Table constraint `UNIQUE(session_id, reviewer_id)` ensuring single review submission per participant.
  - Real-time dynamic calculation of student average ratings and total review counts.
  - Personalized student dashboard with live statistical indicators and interactive Chart.js visualizations.
- **Test Verification:** 100% Passed (17 Unit & Integration Tests).

---

### Module 06: Administration & Platform Governance
- **Tier:** Governance & System Maintenance Tier
- **Routing Endpoints:** `/admin`, `/admin/categories`, `/admin/skills`, `/admin/stats`
- **Controller Blueprint:** `app/routes/admin.py`
- **Service Layer:** Administrative route controllers, CLI subroutines (`app/cli.py`)
- **Entities & Models:** All Models (`User`, `SkillCategory`, `Skill`, `ExchangeRequest`, etc.)
- **Core Capabilities:**
  - Dedicated administrative dashboard protected by `@admin_required` authorization guard.
  - System-wide telemetry metrics (user enrollments, exchange volumes, session completion rates).
  - Skill taxonomy management (creating, editing, and categorizing canonical skills).
  - Quality moderation and curation of student-proposed unlisted skills.
  - CLI operations: `seed-skills` (idempotent population), `create-admin` (bootstrap administrator), `reset-db`.
- **Test Verification:** 100% Passed (CLI & RBAC Tests).
