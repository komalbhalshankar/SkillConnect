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

## 2. Phase 2 Verified Test Execution Report

**Test Run Date:** October 18, 2026  
**Environment:** Python 3.14.7 / pytest 9.1.1 / Flask Test Client  
**Execution Command:** `pytest -v`  
**Overall Result:** **18 Passed, 0 Failed, 0 Errors (100% Pass Rate)**

| Test File | Test Case Name | Objective | Result |
| :--- | :--- | :--- | :---: |
| `tests/test_auth.py` | `test_successful_student_registration` | Valid registration creates user, hashes password, redirects to login | **PASSED** |
| `tests/test_auth.py` | `test_duplicate_email_registration_rejected` | Duplicate email rejected with flash alert | **PASSED** |
| `tests/test_auth.py` | `test_password_hashing_security` | Plaintext never stored; Werkzeug salt & hash verified | **PASSED** |
| `tests/test_auth.py` | `test_successful_login` | Valid credentials establish authenticated Flask-Login session | **PASSED** |
| `tests/test_auth.py` | `test_unsuccessful_login_with_wrong_password` | Incorrect password rejected with error alert | **PASSED** |
| `tests/test_auth.py` | `test_unsuccessful_login_with_unregistered_email` | Nonexistent email rejected | **PASSED** |
| `tests/test_auth.py` | `test_logout` | Session cleared on logout | **PASSED** |
| `tests/test_auth.py` | `test_protected_routes_redirect_unauthenticated_user` | `/dashboard` and `/profile` redirect to `/auth/login` | **PASSED** |
| `tests/test_auth.py` | `test_admin_access_allowed_for_admin_role` | Administrator accesses `/admin` successfully (HTTP 200) | **PASSED** |
| `tests/test_auth.py` | `test_admin_access_forbidden_for_student_role` | Regular student receives HTTP 403 Forbidden on `/admin` | **PASSED** |
| `tests/test_database.py`| `test_user_email_unique_database_constraint` | Database-level unique constraint on User.email enforced | **PASSED** |
| `tests/test_database.py`| `test_skill_category_and_skill_models_relationship` | SkillCategory $\leftrightarrow$ Skill relational primary/foreign keys | **PASSED** |
| `tests/test_database.py`| `test_cli_init_db` | `flask init-db` command creates tables idempotently | **PASSED** |
| `tests/test_database.py`| `test_cli_create_admin` | `flask create-admin` creates admin account without code secrets | **PASSED** |
| `tests/test_profile.py` | `test_view_logged_in_profile` | Authenticated student views personal profile fields | **PASSED** |
| `tests/test_profile.py` | `test_update_profile_success` | Student updates name, college, bio, availability | **PASSED** |
| `tests/test_profile.py` | `test_profile_update_validation_rejects_empty_name` | Server-side validation rejects empty/invalid names | **PASSED** |
| `tests/test_profile.py` | `test_unauthorized_user_cannot_update_other_student_profile` | Ownership enforced; students cannot alter other profiles | **PASSED** |

---

## 3. Future Phases Test Matrix (Scheduled)

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
