# SkillConnect — System Requirements Specification (SRS)
**Version:** 1.0  
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
- Discovers compatible peers, inspects match compatibility scores.
- Sends, receives, accepts, rejects, and cancels skill exchange proposals.
- Schedules, tracks, and completes learning sessions.
- Rates peer exchanges and views analytics on their personalized dashboard.

### 2.2 Administrator Actor
- Elevated privileges user with administrative credentials.
- Accesses a protected admin portal (`/admin`).
- Views global system statistics (user counts, exchanges, sessions, ratings).
- Manages skill categories (create, edit, view) and system-wide standardized skill sets.

---

## 3. Functional Requirements by Module

### Module 1: User Authentication and Profile
- **FR-1.1 Student Registration:** Students register with Name, Email, Password, College, Bio, and Availability schedule.
- **FR-1.2 Unique Email Verification:** System validates email format and enforces strict database uniqueness.
- **FR-1.3 Password Security:** Passwords must be hashed using `werkzeug.security.generate_password_hash` with secure salting. Plaintext passwords must never be stored or logged.
- **FR-1.4 Session Management:** Session authentication powered by `Flask-Login` with `@login_required` route decorators.
- **FR-1.5 Role-Based Access Control (RBAC):** Distinct roles (`student`, `admin`) enforced on both UI and backend controller endpoints.
- **FR-1.6 Profile Management:** Students can view their profile and update their bio, college, and availability schedule at any time.
- **FR-1.7 Safe Validation & Error Messaging:** Server-side validation with user-friendly flash messages for invalid inputs.

### Module 2: Skill Management
- **FR-2.1 Skill Organization:** Skills belong to standardized categories (e.g., Programming & Tech, Design & Creative, Communication & Languages, Academics & Science, Business & Marketing).
- **FR-2.2 Skill Association:** Students link skills to their profile with:
  - Skill Type: `Teach` (skills the student can teach) or `Learn` (skills the student wants to learn).
  - Proficiency Level: `Beginner`, `Intermediate`, or `Advanced`.
  - Optional custom notes on experience or specific learning goals.
- **FR-2.3 Duplicate Prevention:** A student cannot add the same skill twice under the same skill type.
- **FR-2.4 Authorization & Ownership:** Students can edit or delete only their own skill records.
- **FR-2.5 Category Seeding:** Sensible default categories and baseline skills are pre-seeded for initial demonstration.

### Module 3: Skill Discovery and Matching
- **FR-3.1 Search & Filter:** Students can search peers by skill name, and filter by skill category, proficiency level, and exchange role.
- **FR-3.2 Student Profile Inspection:** Students can view peer profiles displaying their college, bio, availability, teach skills, and learn skills.
- **FR-3.3 Deterministic Rule-Based Two-Way Matching:**
  - Evaluates reciprocal synergy: Current Student's Learn skills $\cap$ Target Student's Teach skills, AND Current Student's Teach skills $\cap$ Target Student's Learn skills.
  - Scores reciprocal matches higher than one-way matches.
  - Factors in proficiency levels and category breadth.
  - Bounded strictly between 0% and 100%.
  - Fully deterministic, transparent, and auditable.
- **FR-3.4 Transparent Match Breakdown:** Explains exactly which skills matched in each direction.
- **FR-3.5 Exclude Self:** The currently logged-in student is strictly excluded from matching and peer discovery.
- **FR-3.6 Graceful Empty States:** Handled cleanly when a user has no skills or no matches exist.

### Module 4: Skill Exchange and Session Management
- **FR-4.1 Exchange Request Creation:**
  - Sender initiates a request to a recipient specifying: Offered Skill (what sender will teach), Requested Skill (what sender wants to learn), and an optional introductory message.
  - Enforces: Sender $\neq$ Recipient. Prevents duplicate active pending requests between identical pairs for the same skills.
- **FR-4.2 Request States & Transitions:**
  - Valid states: `Pending`, `Accepted`, `Rejected`, `Cancelled`.
  - Recipient can `Accept` or `Reject` a `Pending` request.
  - Sender can `Cancel` their own `Pending` request.
  - State transitions are idempotent and guarded against tampering.
- **FR-4.3 Session Scheduling:**
  - Sessions can only be scheduled for requests with `Accepted` status.
  - Stores: Date, Start Time, Duration/End Time, Mode (`Online`, `In-Person`, `Hybrid`), Meeting Link / Physical Location, Agenda/Notes.
- **FR-4.4 Session States & Lifecycle:**
  - States: `Scheduled`, `Completed`, `Cancelled`.
  - Either participant can view session details.
  - Eligible participants can mark a session as `Completed` once the session has taken place, or `Cancelled` before completion.
- **FR-4.5 Authorization Guardrails:** Unrelated users cannot view, modify, accept, or cancel requests or sessions.

### Module 5: Rating, Feedback and Dashboard
- **FR-5.1 Post-Session Ratings:**
  - A participant can submit a rating (1 to 5 stars) and qualitative feedback text ONLY after a session is marked `Completed`.
  - Cannot rate pending or cancelled sessions.
- **FR-5.2 Duplicate Prevention:** A user can submit only one rating per completed session exchange.
- **FR-5.3 Aggregate Reputation:** Computes and displays average star ratings and total review counts on student profiles.
- **FR-5.4 Personalized Student Dashboard:**
  - Metrics: Total Skills, Compatible Matches, Pending Requests, Upcoming Sessions, Completed Exchanges, Average Rating.
  - Interactive Chart.js visualizations for activity status distribution and skill portfolio breakdown.
  - Quick action links to active requests and upcoming sessions.
- **FR-5.5 Admin Dashboard:**
  - Platform-wide statistics: Total Registered Students, Total Skills Listed, Total Exchanges Initiated, Total Sessions Completed, Platform Average Rating.
  - Management tables for categories and skills.

---

## 4. Non-Functional Requirements (NFR)
- **NFR-1 Security:** CSRF tokens on all state-altering forms, hashed passwords, parameterized SQL queries via SQLAlchemy ORM, XSS escaping in Jinja2 templates, robust route-level permission decorators.
- **NFR-2 Reliability:** ACID compliance with SQLite transactions; safe database migrations and idempotent initial seeding.
- **NFR-3 Maintainability:** Modular blueprint structure, separation of concerns (Models, Views/Controllers, Services, Forms, Templates), PEP 8 compliance.
- **NFR-4 Performance:** Lightweight pages loading in under 500ms on local environments, minimal external CSS/JS payload (Bootstrap 5 CDN, Chart.js CDN).
- **NFR-5 Extensibility:** Clear service layer abstraction to allow adding notifications, messaging, or advanced scheduling in future releases without modifying core models.
