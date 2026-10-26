# SkillConnect — Database Data Dictionary

**Project:** SkillConnect — Peer-to-Peer Student Skill Exchange Platform  
**Program:** MCA Semester 1 Mini Project  
**Database Engine:** SQLite 3 (Third Normal Form - 3NF)  
**ORM Framework:** SQLAlchemy 2.0+ via Flask-SQLAlchemy 3.1+  
**Visual Artifacts:**
- **Entity-Relationship (ER) Diagram (PNG):** [database_er_diagram.png](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/database_er_diagram.png) (Visual relational schema)
- **Entity-Relationship (ER) Diagram (SVG):** [database_er_diagram.svg](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/database_er_diagram.svg) (Lossless vector graphic)
- **Official Print-Ready PDF:** [SkillConnect_Data_Dictionary.pdf](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/SkillConnect_Data_Dictionary.pdf) (High-fidelity, vectorized A4 PDF)
- **High-Resolution PNG:** [data_dictionary.png](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/data_dictionary.png) (1750 &times; 3561 px)
- **Scalable Vector Graphic (SVG):** [data_dictionary.svg](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/data_dictionary.svg) (Lossless vector image)
- **Interactive Web Viewer:** [data_dictionary.html](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/data_dictionary.html) (Searchable, filterable, one-click downloads)
- **UML Diagrams Hub:** [diagrams_viewer.html](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/diagrams_viewer.html)

---

## 1. Visual Specification (Image Preview)

![SkillConnect Data Dictionary Image Preview](file:///d:/MCA/Python_Mini_Project_Sem%20l/docs/data_dictionary.png)

---

## 2. Relational Summary Matrix

| # | Table Name | Category | Primary Key | Foreign Keys | Unique Constraints | Purpose |
| :- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | `users` | Core / Identity | `id` | None | `email` | User profiles, student/admin roles, authentication |
| **2** | `skill_categories` | Taxonomy | `id` | None | `name` | Disciplines for grouping skills (Programming, DB, Design) |
| **3** | `skills` | Catalogue | `id` | `category_id` | `name` | Canonical catalogue of available platform skills |
| **4** | `user_skills` | Associative / Junction | `id` | `user_id`, `skill_id` | `(user_id, skill_id, skill_type)` | Student skill offerings and learning objectives |
| **5** | `exchange_requests` | Workflow / Proposal | `id` | `sender_id`, `receiver_id`, `offered_skill_id`, `requested_skill_id` | None | Bilateral peer skill exchange proposals |
| **6** | `exchange_sessions` | Workflow / Operations | `id` | `request_id` | `request_id` | Scheduled learning sessions resulting from accepted proposals |
| **7** | `ratings` | Evaluation / Feedback | `id` | `session_id`, `reviewer_id`, `reviewee_id` | `(session_id, reviewer_id)` | Post-session peer feedback and 1-5 star ratings |

---

## 3. Comprehensive Data Dictionary Tables

### 3.1 Table: `users`
Stores student and administrator credentials, profiles, and roles.

| Column | Type | Constraints | Nullable | Default | Description & Business Rules |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | NO | None | Unique system identifier for user |
| `name` | VARCHAR(120) | NOT NULL | NO | None | Full legal or display name of student / admin |
| `email` | VARCHAR(180) | NOT NULL, UNIQUE, INDEX | NO | None | Institutional email address (login credential) |
| `password_hash` | VARCHAR(255) | NOT NULL | NO | None | Salted cryptographic password hash (`pbkdf2:sha256`) |
| `role` | VARCHAR(20) | NOT NULL | NO | `'student'` | Authorization role: `'student'` or `'admin'` |
| `college` | VARCHAR(180) | NULLABLE | YES | None | Enrolled university / college institution name |
| `bio` | TEXT | NULLABLE | YES | None | Student biography, academic interests & background |
| `availability` | VARCHAR(120) | NULLABLE | YES | None | Preferred study hours (e.g., "Weekends & Evenings") |
| `created_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Account registration timestamp (UTC) |
| `updated_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Last profile update timestamp (UTC, onupdate) |

- **Foreign Key Relationships:**
  - One-to-Many: `user_skills` (`UserSkill.user_id`)
  - One-to-Many: `sent_requests` (`ExchangeRequest.sender_id`)
  - One-to-Many: `received_requests` (`ExchangeRequest.receiver_id`)
  - One-to-Many: `given_ratings` (`Rating.reviewer_id`)
  - One-to-Many: `received_ratings` (`Rating.reviewee_id`)

---

### 3.2 Table: `skill_categories`
Taxonomy groupings for organizing skills into academic disciplines.

| Column | Type | Constraints | Nullable | Default | Description & Business Rules |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | NO | None | Unique taxonomy category identifier |
| `name` | VARCHAR(80) | NOT NULL, UNIQUE | NO | None | Category name (e.g., "Programming & Tech", "Database", "Design") |
| `description` | VARCHAR(255) | NULLABLE | YES | None | Overview of domain skills covered in this category |
| `icon` | VARCHAR(50) | NOT NULL | NO | `'bi-tag'` | Bootstrap Icons CSS class for UI visual badge |
| `created_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Taxonomy creation timestamp (UTC) |

- **Foreign Key Relationships:**
  - One-to-Many: `skills` (`Skill.category_id`) with cascade `all, delete-orphan`

---

### 3.3 Table: `skills`
Standardized catalog of skills available on the platform.

| Column | Type | Constraints | Nullable | Default | Description & Business Rules |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | NO | None | Unique skill primary identifier |
| `category_id` | INTEGER | NOT NULL, FOREIGN KEY | NO | None | Parent category ID referencing `skill_categories.id` |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE, INDEX | NO | None | Canonical skill name (e.g. "Python", "SQL", "Figma") |
| `description` | VARCHAR(255) | NULLABLE | YES | None | Summary curriculum or domain details |
| `created_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Skill registration timestamp (UTC) |

- **Deduplication Policy:** Case-insensitive lookup reuses existing `Skill` records when students propose new skills.

---

### 3.4 Table: `user_skills`
Junction table mapping student profiles to skills with teaching/learning intent and proficiency.

| Column | Type | Constraints | Nullable | Default | Description & Business Rules |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | NO | None | Unique junction record identifier |
| `user_id` | INTEGER | NOT NULL, FOREIGN KEY, INDEX | NO | None | Student ID referencing `users.id` |
| `skill_id` | INTEGER | NOT NULL, FOREIGN KEY, INDEX | NO | None | Skill ID referencing `skills.id` |
| `skill_type` | VARCHAR(10) | NOT NULL | NO | None | Intent type: `'teach'` (offered) or `'learn'` (desired) |
| `proficiency` | VARCHAR(20) | NOT NULL | NO | `'intermediate'` | Proficiency level: `'beginner'`, `'intermediate'`, `'advanced'` |
| `notes` | VARCHAR(255) | NULLABLE | YES | None | Specific student notes, framework focus, or topics |
| `created_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Record creation timestamp (UTC) |
| `updated_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Record last updated timestamp (UTC, onupdate) |

- **Composite Constraint:** `UNIQUE(user_id, skill_id, skill_type)` (`uq_user_skill_type`) prevents duplicate skill additions under the same intent.

---

### 3.5 Table: `exchange_requests`
Bilateral skill exchange proposals between students.

| Column | Type | Constraints | Nullable | Default | Description & Business Rules |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | NO | None | Unique exchange proposal identifier |
| `sender_id` | INTEGER | NOT NULL, FOREIGN KEY, INDEX | NO | None | Initiator student ID referencing `users.id` |
| `receiver_id` | INTEGER | NOT NULL, FOREIGN KEY, INDEX | NO | None | Target peer student ID referencing `users.id` |
| `offered_skill_id` | INTEGER | NOT NULL, FOREIGN KEY | NO | None | Skill sender promises to teach referencing `skills.id` |
| `requested_skill_id` | INTEGER | NOT NULL, FOREIGN KEY | NO | None | Skill sender desires to learn referencing `skills.id` |
| `status` | VARCHAR(20) | NOT NULL | NO | `'pending'` | State: `'pending'`, `'accepted'`, `'rejected'`, `'cancelled'` |
| `message` | TEXT | NULLABLE | YES | None | Personal introductory note and schedule preferences |
| `created_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Proposal sent timestamp (UTC) |
| `updated_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Status change timestamp (UTC, onupdate) |

- **Integrity Constraint:** Service and database validation enforce `sender_id != receiver_id` preventing self-proposals.

---

### 3.6 Table: `exchange_sessions`
Scheduled learning meetings originating from accepted exchange requests.

| Column | Type | Constraints | Nullable | Default | Description & Business Rules |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | NO | None | Unique session identifier |
| `request_id` | INTEGER | NOT NULL, UNIQUE, FOREIGN KEY | NO | None | Parent accepted request referencing `exchange_requests.id` |
| `scheduled_at` | DATETIME | NOT NULL | NO | None | Date and time of scheduled session |
| `duration_minutes` | INTEGER | NOT NULL | NO | `60` | Planned meeting duration in minutes |
| `mode` | VARCHAR(20) | NOT NULL | NO | `'online'` | Delivery mode: `'online'`, `'in_person'`, `'hybrid'` |
| `meeting_details` | VARCHAR(255) | NULLABLE | YES | None | Video call URL (Google Meet / Zoom) or campus room |
| `notes` | TEXT | NULLABLE | YES | None | Session agenda, preparation links, or homework notes |
| `status` | VARCHAR(20) | NOT NULL | NO | `'scheduled'` | Session state: `'scheduled'`, `'completed'`, `'cancelled'` |
| `created_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Session booking timestamp (UTC) |
| `updated_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Last session update timestamp (UTC, onupdate) |

- **Unique Constraint:** `UNIQUE(request_id)` enforces strict 1-to-1 relationship with accepted proposals. In-place rescheduling is supported after cancellation.

---

### 3.7 Table: `ratings`
Mutual post-session peer ratings and qualitative evaluations.

| Column | Type | Constraints | Nullable | Default | Description & Business Rules |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | NO | None | Unique rating identifier |
| `session_id` | INTEGER | NOT NULL, FOREIGN KEY, INDEX | NO | None | Completed session ID referencing `exchange_sessions.id` |
| `reviewer_id` | INTEGER | NOT NULL, FOREIGN KEY, INDEX | NO | None | Student authoring rating referencing `users.id` |
| `reviewee_id` | INTEGER | NOT NULL, FOREIGN KEY, INDEX | NO | None | Student receiving rating referencing `users.id` |
| `score` | INTEGER | NOT NULL, CHECK 1..5 | NO | None | Numerical evaluation score (1 to 5 stars) |
| `feedback` | TEXT | NULLABLE | YES | None | Qualitative peer feedback and remarks |
| `created_at` | DATETIME | NOT NULL | NO | `UTC_NOW` | Rating submission timestamp (UTC) |

- **Composite Constraints:**
  - `UNIQUE(session_id, reviewer_id)` (`uq_session_reviewer`) ensures each participant can evaluate a session at most once.
  - `CHECK(score >= 1 AND score <= 5)` (`ck_rating_score_range`) enforces valid rating range.
  - Ratings can only be submitted when `exchange_sessions.status == 'completed'`.
