# SkillConnect — Comprehensive Test Plan
**Version:** 1.0  
**Test Framework:** `pytest` (v9+) & Flask Test Client  
**Database Isolation:** In-Memory SQLite (`sqlite:///:memory:`)  

---

## 1. Test Strategy & Isolation Philosophy
1. **Zero Contamination:** Test executions run against an isolated in-memory SQLite database (`sqlite:///:memory:`). The developer's persistent instance database (`instance/skillconnect.db`) is untouched during test runs.
2. **Determinism:** Tests setup fresh database schema fixtures (`db.create_all()` / `db.drop_all()`) per test function.
3. **Layered Coverage:** Tests exercise both the Service Layer (unit business logic) and Flask Blueprints (integration tests with HTTP status codes, form validations, session state, and redirects).

---

## 2. Test Suites Matrix

### Suite 1: Authentication & Access Control (`tests/test_auth.py`)
| Test ID | Objective | Expected Result |
| :--- | :--- | :--- |
| `test_user_registration_success` | Register a new student with valid inputs | User created, password securely hashed, redirect to login |
| `test_duplicate_email_registration` | Attempt registration with an existing email | Registration rejected with descriptive error message |
| `test_user_login_and_logout` | Log in with valid credentials and log out | Session established on login, session cleared on logout |
| `test_invalid_credentials_login` | Attempt login with wrong password | 401/Flash error, authentication denied |
| `test_protected_routes_unauthenticated` | Access `/dashboard`, `/skills`, `/exchanges` when logged out | Redirected to `/auth/login` |
| `test_profile_update` | Modify bio, college, and availability | Profile changes persisted in database |

### Suite 2: Skill Portfolio Management (`tests/test_skills.py`)
| Test ID | Objective | Expected Result |
| :--- | :--- | :--- |
| `test_add_teach_and_learn_skill` | Add a teach skill and a learn skill | Distinct `user_skills` records created |
| `test_prevent_duplicate_skill_entry` | Add the same skill under the same type twice | Rejected by unique constraint / service validation |
| `test_edit_skill_proficiency` | Change proficiency from Beginner to Advanced | Updated proficiency reflected in query |
| `test_skill_ownership_enforcement` | User B attempts to edit or delete User A's skill | Forbidden (403 or denied) |
| `test_remove_skill` | Delete owned skill | Record removed from `user_skills` |

### Suite 3: Skill Discovery & Matching Engine (`tests/test_matching.py`)
| Test ID | Objective | Expected Result |
| :--- | :--- | :--- |
| `test_reciprocal_matching_score` | User A (Teaches Python, Learns UI) & User B (Teaches UI, Learns Python) | Score $\ge 60\%$, marked Reciprocal, exact matching skills listed |
| `test_one_way_matching_score` | User A (Learns Python) & User B (Teaches Python, Learns Chess) | Score between 30% and 55%, marked One-Way |
| `test_zero_overlap_excluded` | User A and User C have completely disjoint skills | User C is excluded from recommendations |
| `test_self_exclusion` | Current user runs match recommendation | Current user is never in the match list |
| `test_score_bounding` | Extreme skill overlap combinations | Score stays strictly within $[0, 100]$ |
| `test_search_and_filter_skills` | Search by name and filter by category | Returns only matching students |

### Suite 4: Exchange Requests & Sessions (`tests/test_exchanges.py`)
| Test ID | Objective | Expected Result |
| :--- | :--- | :--- |
| `test_create_exchange_request` | Send proposal with offered & requested skill | Record created with status `Pending` |
| `test_prevent_self_exchange_request` | Attempt to send request to oneself | Validation error, request blocked |
| `test_accept_exchange_request` | Recipient accepts pending request | Status transitions to `Accepted` |
| `test_reject_exchange_request` | Recipient rejects pending request | Status transitions to `Rejected` |
| `test_cancel_exchange_request` | Sender cancels pending request | Status transitions to `Cancelled` |
| `test_schedule_session_for_accepted_request` | Schedule meeting for accepted request | Session created with status `Scheduled` |
| `test_prevent_session_for_pending_request` | Attempt to schedule session before acceptance | Blocked with validation error |
| `test_complete_and_cancel_session` | Complete or cancel scheduled session | Valid status transition |
| `test_unauthorized_session_tampering` | Third party attempts to modify session | Blocked / Unauthorized |

### Suite 5: Rating, Feedback & Dashboard (`tests/test_ratings.py`)
| Test ID | Objective | Expected Result |
| :--- | :--- | :--- |
| `test_rate_completed_session` | Participant rates finished session (1–5) | Rating record created, average updated |
| `test_prevent_rating_uncompleted_session` | Attempt to rate scheduled/cancelled session | Blocked |
| `test_prevent_duplicate_rating` | Same reviewer rates same session twice | Blocked by unique constraint |
| `test_student_dashboard_metrics` | Calculate dashboard counters | Accurate counts for skills, sessions, matches |

### Suite 6: Platform Administration (`tests/test_admin.py`)
| Test ID | Objective | Expected Result |
| :--- | :--- | :--- |
| `test_admin_portal_access_admin_role` | Admin accesses `/admin` | HTTP 200, stats displayed |
| `test_admin_portal_access_student_role` | Regular student accesses `/admin` | HTTP 403 Forbidden |
| `test_admin_manage_categories` | Admin creates/edits skill category | Category saved and available in taxonomy |
