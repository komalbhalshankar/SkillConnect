# SkillConnect — UML Class Diagram Specification
**Academic Level:** MCA Semester 1 — Python Mini Project  
**System Boundary:** `SkillConnect Platform`  
**Pattern:** Layered MVC Architecture with Service Layer & SQLAlchemy ORM  
**Current Baseline:** Fully implemented & verified (96/96 unit/integration tests passing)

---

## 1. Overview
The **SkillConnect Class Diagram** models the static structure of the application. It captures:
1. **Domain Entities (Data Layer):** SQLAlchemy ORM models mapped directly to normalized relational tables (3NF).
2. **Service Layer (Domain Logic):** Dedicated business logic classes encapsulating matching logic, request state machines, session management, and rating computations.
3. **Relationships & Multiplicities:** 1-to-1, 1-to-many, composition, associative entities, and service-to-model dependencies.

- **High-Resolution PNG:** [class_diagram.png](class_diagram.png) (UML Class Diagram)
- **Scalable Vector Graphic:** [class_diagram.svg](class_diagram.svg)
- **PlantUML Source:** [class_diagram.puml](class_diagram.puml)

![SkillConnect UML Class Diagram](class_diagram.png)

---

## 2. Mermaid Class Diagram

```mermaid
classDiagram
    direction TB

    %% ==========================================
    %% DOMAIN ENTITY / MODEL TIER
    %% ==========================================

    class User {
        +int id
        +string name
        +string email
        +string password_hash
        +string role
        +string college
        +string bio
        +string availability
        +datetime created_at
        +datetime updated_at
        +set_password(password: str) void
        +check_password(password: str) bool
        +is_admin() bool
        +teach_skills() list~UserSkill~
        +learn_skills() list~UserSkill~
        +average_rating() float
        +review_count() int
    }

    class SkillCategory {
        +int id
        +string name
        +string description
        +string icon
        +datetime created_at
    }

    class Skill {
        +int id
        +int category_id
        +string name
        +string description
        +datetime created_at
    }

    class UserSkill {
        +int id
        +int user_id
        +int skill_id
        +string skill_type
        +string proficiency
        +string notes
        +datetime created_at
        +datetime updated_at
        +proficiency_weight() int
    }

    class ExchangeRequest {
        +int id
        +int sender_id
        +int receiver_id
        +int offered_skill_id
        +int requested_skill_id
        +string status
        +string message
        +datetime created_at
        +datetime updated_at
        +is_pending() bool
        +is_accepted() bool
        +is_rejected() bool
        +is_cancelled() bool
        +status_badge_class() str
        +partner(user_id: int) User
        +is_participant(user_id: int) bool
    }

    class ExchangeSession {
        +int id
        +int request_id
        +datetime scheduled_at
        +int duration_minutes
        +string mode
        +string meeting_details
        +string notes
        +string status
        +datetime created_at
        +datetime updated_at
        +is_scheduled() bool
        +is_completed() bool
        +is_cancelled() bool
        +status_badge_class() str
        +formatted_date() str
        +formatted_time() str
        +is_participant(user_id: int) bool
        +partner(user_id: int) User
        +has_user_rated(user_id: int) bool
        +get_user_rating(user_id: int) Rating
    }

    class Rating {
        +int id
        +int session_id
        +int reviewer_id
        +int reviewee_id
        +int score
        +string feedback
        +datetime created_at
    }

    %% ==========================================
    %% SERVICE / BUSINESS LOGIC TIER
    %% ==========================================

    class AuthService {
        +register_user(name, email, password, college) tuple
        +authenticate_user(email, password) User
        +update_profile(user_id, name, college, bio, availability) tuple
        +change_password(user_id, old_pw, new_pw) tuple
        +delete_student(user_id) tuple
    }

    class SkillService {
        +get_all_categories() list~SkillCategory~
        +get_all_skills() list~Skill~
        +get_skills_by_category(category_id) list~Skill~
        +get_user_skills(user_id, skill_type) list~UserSkill~
        +add_user_skill(user_id, skill_id, skill_type, proficiency, notes, custom_name, cat_id) tuple
        +remove_user_skill(user_skill_id, user_id) tuple
        +update_user_skill(user_skill_id, user_id, proficiency, notes) tuple
        +search_students(query, skill_id, category_id, skill_type) list
        +delete_category(category_id) tuple
        +delete_standard_skill(skill_id) tuple
    }

    class MatchingService {
        +calculate_compatibility(user_a, user_b) dict
        +find_matches(user, category_id, min_score, page, per_page) list
        +get_top_matches(user, limit) list
    }

    class ExchangeService {
        +create_request(sender_id, receiver_id, offered_skill_id, requested_skill_id, msg) tuple
        +respond_to_request(request_id, user_id, action) tuple
        +cancel_request(request_id, user_id) tuple
        +schedule_session(request_id, user_id, scheduled_at, duration, mode, details, notes) tuple
        +complete_session(session_id, user_id) tuple
        +cancel_session(session_id, user_id) tuple
        +get_user_requests(user_id, status_filter) list
        +get_user_sessions(user_id, status_filter) list
    }

    class RatingService {
        +submit_rating(session_id, reviewer_id, score, feedback) tuple
        +get_user_ratings(user_id) list
        +get_session_ratings(session_id) list
    }

    class StatsService {
        +get_student_dashboard_stats(user_id) dict
        +get_admin_stats() dict
    }

    %% ==========================================
    %% RELATIONSHIPS & MULTIPLICITIES
    %% ==========================================

    %% User to UserSkill (One-to-Many Composition)
    User "1" *-- "0..*" UserSkill : owns / declares

    %% Category to Skill (One-to-Many Composition)
    SkillCategory "1" *-- "0..*" Skill : classifies

    %% Skill to UserSkill (One-to-Many Association)
    Skill "1" -- "0..*" UserSkill : referenced_by

    %% User to ExchangeRequest (One-to-Many Association)
    User "1" -- "0..*" ExchangeRequest : sends (sender)
    User "1" -- "0..*" ExchangeRequest : receives (receiver)

    %% Skill to ExchangeRequest (One-to-Many Association)
    Skill "1" -- "0..*" ExchangeRequest : offered_skill
    Skill "1" -- "0..*" ExchangeRequest : requested_skill

    %% ExchangeRequest to ExchangeSession (1-to-0..1 Composition)
    ExchangeRequest "1" *-- "0..1" ExchangeSession : schedules

    %% ExchangeSession to Rating (1-to-0..2 Composition)
    ExchangeSession "1" *-- "0..2" Rating : evaluated_by

    %% User to Rating (One-to-Many Association)
    User "1" -- "0..*" Rating : reviews (reviewer)
    User "1" -- "0..*" Rating : reviewed (reviewee)

    %% ==========================================
    %% SERVICE DEPENDENCIES
    %% ==========================================
    AuthService ..> User : manages
    SkillService ..> SkillCategory : queries
    SkillService ..> Skill : manages
    SkillService ..> UserSkill : manages
    MatchingService ..> User : inspects
    MatchingService ..> UserSkill : evaluates
    ExchangeService ..> ExchangeRequest : controls state
    ExchangeService ..> ExchangeSession : controls lifecycle
    RatingService ..> Rating : creates & computes
    RatingService ..> ExchangeSession : verifies status
    StatsService ..> User : aggregates
    StatsService ..> ExchangeSession : aggregates
```

---

## 3. Structural Analysis of Key Classes

### 3.1 Domain Entity Layer

#### 1. `User` (extends `UserMixin`, `db.Model`)
- **Responsibility:** Represents authenticated actors (students and admins).
- **Key Attributes:** `id`, `name`, `email` (unique index), `password_hash`, `role` (`student` or `admin`), `college`, `bio`, `availability`.
- **Key Methods / Properties:**
  - `set_password(password)`: Hashes plaintext password using `werkzeug.security`.
  - `check_password(password)`: Verifies candidate credentials.
  - `is_admin`: Boolean flag for administrative RBAC.
  - `teach_skills`: Dynamic filter for user skills marked with `skill_type = 'teach'`.
  - `learn_skills`: Dynamic filter for user skills marked with `skill_type = 'learn'`.
  - `average_rating`: Aggregates received ratings rounded to 1 decimal place.

#### 2. `SkillCategory` & `Skill`
- **Responsibility:** Normalized catalog taxonomy.
- **Multiplicity:** 1 `SkillCategory` contains $0..*$ `Skill`s (`cascade="all, delete-orphan"`).
- **Attributes:** Unique category names, UI Bootstrap icons, normalized skill names indexed for rapid search.

#### 3. `UserSkill` (Associative Entity)
- **Responsibility:** Models the Many-to-Many relationship between `User` and `Skill` with rich attributes.
- **Attributes:** `skill_type` (`teach` or `learn`), `proficiency` (`beginner`, `intermediate`, `advanced`), `notes`.
- **Unique Constraint:** `(user_id, skill_id, skill_type)` ensures a student cannot add the exact same skill twice for the same portfolio role.
- **Method:** `proficiency_weight` maps strings to ordinal weights (1, 2, 3) for algorithmic ranking.

#### 4. `ExchangeRequest`
- **Responsibility:** Bilateral skill exchange contract proposal.
- **State Machine:** `status IN ('pending', 'accepted', 'rejected', 'cancelled')`.
- **Foreign Keys:** `sender_id`, `receiver_id`, `offered_skill_id`, `requested_skill_id`.
- **Methods:** `partner(current_user_id)`, `is_participant(user_id)`.

#### 5. `ExchangeSession`
- **Responsibility:** Temporal scheduling and fulfillment of an accepted exchange.
- **Multiplicity:** Strict 1-to-1 relationship with `ExchangeRequest` via unique foreign key `request_id`.
- **State Machine:** `status IN ('scheduled', 'completed', 'cancelled')`.
- **Methods:** `is_participant(user_id)`, `has_user_rated(user_id)`, `get_user_rating(user_id)`.

#### 6. `Rating`
- **Responsibility:** Bilateral evaluation and feedback after session completion.
- **Constraints:**
  - Check constraint: `1 <= score <= 5`.
  - Unique constraint: `(session_id, reviewer_id)` prevents ballot stuffing.
- **Multiplicity:** At most 2 ratings per session (one from each participant).

---

## 4. Multiplicity Summary Table

| Relationship | Type | Multiplicity | Rationale |
|---|---|---|---|
| `User` $\rightarrow$ `UserSkill` | Composition | $1 \text{ to } 0..*$ | Deleting a user cascades and removes their skill portfolio. |
| `SkillCategory` $\rightarrow$ `Skill` | Composition | $1 \text{ to } 0..*$ | Deleting a category removes all its classified skills. |
| `Skill` $\rightarrow$ `UserSkill` | Association | $1 \text{ to } 0..*$ | A skill can be offered or sought by many students. |
| `User` $\rightarrow$ `ExchangeRequest` | Association | $1 \text{ to } 0..*$ | A student can send and receive multiple exchange requests. |
| `ExchangeRequest` $\rightarrow$ `ExchangeSession` | Composition | $1 \text{ to } 0..1$ | An accepted request has at most one active session schedule. |
| `ExchangeSession` $\rightarrow$ `Rating` | Composition | $1 \text{ to } 0..2$ | Each completed session allows at most 1 rating per participant. |
| `User` $\rightarrow$ `Rating` | Association | $1 \text{ to } 0..*$ | A user accumulates ratings as reviewer and reviewee. |
