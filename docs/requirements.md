# SkillConnect — System Requirements Specification (SRS)
**Version:** 2.0 (Phase 3 Verified)  
**Project:** SkillConnect — Student Skill Exchange Platform  
**Target Environment:** Python 3.14 / Flask / SQLite / Bootstrap 5 / Vanilla JS / Chart.js  

---

## 1. Executive Summary & Purpose
**SkillConnect** is a web-based peer-to-peer student skill exchange platform designed to enable college students to teach skills they possess and learn skills they wish to acquire. The platform fosters collaborative learning without financial barriers by facilitating mutual knowledge exchange.

The initial Version 1.0 release is structured into five cohesive modules:
1. **User Authentication & Profile**
2. **Skill Management**
3. **Skill Discovery & Matching**
4. **Skill Exchange & Session Management**
5. **Rating, Feedback & Dashboard**

---

## 2. System Actors & Roles

### 2.1 Student Actor
- Standard registered peer learner/teacher.
- Manages personal profile, Teach and Learn skill portfolios.
- Discovers compatible peers via database-backed search and filters.
- Views rule-based matching recommendations with transparent compatibility scores and explanations.
- Inspects peer student profiles.
- *(Future Phase 4 & 5)*: Sends, receives, accepts, rejects, and cancels skill exchange proposals; schedules sessions; rates exchanges and views dashboard analytics.

### 2.2 Administrator Actor
- Elevated privileges user with administrative credentials.
- Accesses a protected admin portal (`/admin`).
- Views global system statistics (user counts, skills, categories).
- Manages skill categories (create, edit, view) and system-wide standardized skill sets.

---

## 3. Implementation Status Matrix (By Phase)

| Module | Core Features | Target Phase | Implementation Status | Test Coverage |
| :--- | :--- | :---: | :---: | :---: |
| **Module 1: User Auth & Profile** | Registration, Login, Logout, RBAC, Profile View/Edit | Phase 2 | **Implemented & Verified** | 100% (Unit & Integration) |
| **Database Foundation** | SQLite schema, User, SkillCategory, Skill, UserSkill models | Phase 2 | **Implemented & Verified** | 100% (Model constraints & CLI) |
| **Module 2: Skill Management** | Add/Edit/Delete Teach & Learn Skills, Taxonomy, Admin Curation | Phase 3 | **Implemented & Verified** | 100% (19 Unit & Integration tests) |
| **Module 3: Discovery & Matching** | Deterministic two-way matching engine, Directory, Profiles | Phase 3 | **Implemented & Verified** | 100% (12 Unit & Integration tests) |
| **Module 4: Exchange & Session** | Exchange proposals, State machine, Scheduling | Phase 4 | *Planned* | Scheduled for Phase 4 |
| **Module 5: Rating & Dashboard** | Post-session reviews, Star ratings, Chart.js feeds | Phase 5 | *Planned* | Scheduled for Phase 5 |
| **Administration** | Safe CLI admin creation (`create-admin`), `@admin_required`, Category/Skill CRUD | Phase 2 & 3 | **Implemented & Verified** | 100% (CLI & RBAC) |

**Total Verified Tests:** 49 tests passing (100% pass rate).

---

## 4. Functional Requirements by Module

### Module 1: User Authentication and Profile
- **FR-1.1 Student Registration:** Students register with Name, Email, Password, College, Bio, and Availability schedule. *(Status: Implemented & Tested)*
- **FR-1.2 Unique Email Verification:** System validates email format and enforces strict database uniqueness. *(Status: Implemented & Tested)*
- **FR-1.3 Password Security:** Passwords must be hashed using `werkzeug.security.generate_password_hash` with secure salting. Plaintext passwords must never be stored or logged. *(Status: Implemented & Tested)*
- **FR-1.4 Session Management:** Session authentication powered by `Flask-Login` with `@login_required` route decorators. *(Status: Implemented & Tested)*
- **FR-1.5 Role-Based Access Control (RBAC):** Distinct roles (`student`, `admin`) enforced on both UI and backend controller endpoints. *(Status: Implemented & Tested)*
- **FR-1.6 Profile Management:** Students can view their profile and update their bio, college, and availability schedule at any time. *(Status: Implemented & Tested)*
- **FR-1.7 Safe Validation & Error Messaging:** Server-side validation with user-friendly flash messages for invalid inputs. *(Status: Implemented & Tested)*

### Module 2: Skill Management
- **FR-2.1 Skill Organization:** Skills belong to standardized categories (Programming, Database, Web Development, Design, Communication, Other). *(Status: Implemented & Tested)*
- **FR-2.2 Skill Association:** Students link skills to their profile with:
  - Skill Type: `Teach` (skills the student can teach) or `Learn` (skills the student wants to learn).
  - Proficiency Level: `Beginner`, `Intermediate`, or `Advanced`.
  - Custom unlisted skill support: Students can enter a custom skill with category assignment; existing skills are reused case-insensitively to prevent uncontrolled duplicates.
  - Optional custom notes on experience or specific learning goals. *(Status: Implemented & Tested)*
- **FR-2.3 Duplicate Prevention:** A student cannot add the same skill twice under the same skill type. A student may associate the same skill with both TEACH and LEARN (e.g., teaching beginner concepts while seeking advanced mentorship). *(Status: Implemented & Tested)*
- **FR-2.4 Authorization & Ownership:** Students can edit or delete only their own skill records; cross-user edits/deletions trigger HTTP 403 Forbidden. *(Status: Implemented & Tested)*
- **FR-2.5 Category Seeding & Admin Curation:** Idempotent CLI seeding command (`flask seed-skills`) and Admin portal category/skill CRUD routes. *(Status: Implemented & Tested)*

### Module 3: Skill Discovery and Matching
- **FR-3.1 Search & Filter:** Students can search peers by skill name, and filter by skill category, proficiency level, and intent (`teach`, `learn`, or `all`). *(Status: Implemented & Tested)*
- **FR-3.2 Student Profile Inspection:** Students can view peer profiles displaying their college, bio, availability, teach skills, learn skills, and bilateral compatibility overview. *(Status: Implemented & Tested)*
- **FR-3.3 Deterministic Rule-Based Two-Way Matching:**
  - Evaluates reciprocal synergy: Current Student's Learn skills $\cap$ Target Student's Teach skills (40 pts), AND Current Student's Teach skills $\cap$ Target Student's Learn skills (40 pts).
  - Relevant category compatibility bonus (+10 pts).
  - Proficiency compatibility bonus (+10 pts when teacher level $\ge$ learner level).
  - Bounded strictly between 0% and 100%.
  - Fully deterministic, transparent, and auditable. *(Status: Implemented & Tested)*
- **FR-3.4 Transparent Match Breakdown:** Explains exactly which skills matched in each direction with an itemized points summary. *(Status: Implemented & Tested)*
- **FR-3.5 Exclude Self:** The currently logged-in student is strictly excluded from matching recommendations and discovery directory. *(Status: Implemented & Tested)*
- **FR-3.6 Graceful Empty States:** Handled cleanly with actionable prompts when a user has no skills or no matches exist. *(Status: Implemented & Tested)*

### Module 4: Skill Exchange and Session Management (Phase 4 Planned)
- **FR-4.1 Exchange Request Creation:**
  - Sender initiates a request to a recipient specifying: Offered Skill, Requested Skill, and an optional introductory message.
  - Enforces: Sender $\neq$ Recipient. Prevents duplicate active pending requests. *(Phase 4)*
- **FR-4.2 Request States & Transitions:**
  - Valid states: `Pending`, `Accepted`, `Rejected`, `Cancelled`.
  - Recipient can `Accept` or `Reject` a `Pending` request.
  - Sender can `Cancel` their own `Pending` request. *(Phase 4)*
- **FR-4.3 Session Scheduling:**
  - Sessions can only be scheduled for requests with `Accepted` status.
  - Stores: Date, Start Time, Duration/End Time, Mode (`Online`, `In-Person`, `Hybrid`), Meeting Link / Physical Location, Agenda/Notes. *(Phase 4)*
- **FR-4.4 Session States & Lifecycle:**
  - States: `Scheduled`, `Completed`, `Cancelled`.
  - Eligible participants can mark a session as `Completed` or `Cancelled`. *(Phase 4)*
- **FR-4.5 Authorization Guardrails:** Unrelated users cannot view, modify, accept, or cancel requests or sessions. *(Phase 4)*

### Module 5: Rating, Feedback and Dashboard (Phase 5 Planned)
- **FR-5.1 Post-Session Ratings:**
  - A participant can submit a rating (1 to 5 stars) and qualitative feedback text ONLY after a session is marked `Completed`. *(Phase 5)*
- **FR-5.2 Duplicate Prevention:** A user can submit only one rating per completed session exchange. *(Phase 5)*
- **FR-5.3 Aggregate Reputation:** Computes and displays average star ratings and total review counts on student profiles. *(Phase 5)*
- **FR-5.4 Personalized Student Dashboard:**
  - Metrics: Total Skills, Compatible Matches, Pending Requests, Upcoming Sessions, Completed Exchanges, Average Rating.
  - Interactive Chart.js visualizations for activity status distribution and skill portfolio breakdown. *(Phase 5)*
- **FR-5.5 Admin Dashboard:**
  - Platform-wide statistics: Total Registered Students, Total Skills Listed, Total Exchanges Initiated, Total Sessions Completed, Platform Average Rating. *(Phase 5)*

---

## 5. Non-Functional Requirements (NFR)
- **NFR-1 Security:** CSRF tokens on all state-altering forms, hashed passwords, parameterized SQL queries via SQLAlchemy ORM, XSS escaping in Jinja2 templates, robust route-level permission decorators.
- **NFR-2 Reliability:** ACID compliance with SQLite transactions; safe database migrations and idempotent initial seeding.
- **NFR-3 Maintainability:** Modular blueprint structure, separation of concerns (Models, Views/Controllers, Services, Forms, Templates), PEP 8 compliance.
- **NFR-4 Performance:** Lightweight pages loading in under 500ms on local environments, minimal external CSS/JS payload (Bootstrap 5 CDN, Chart.js CDN).
- **NFR-5 Extensibility:** Clear service layer abstraction to allow adding exchange workflow, session scheduling, and analytics without modifying core models.
