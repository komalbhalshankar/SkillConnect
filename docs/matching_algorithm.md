# SkillConnect — Deterministic Rule-Based Skill Matching Engine Specification
**Version:** 2.0 (Phase 3 Verified)  
**Methodology:** Deterministic, Rule-Based Bilateral & Unilateral Compatibility Engine  
**Implementation Source:** [`app/services/matching_service.py`](file:///d:/MCA/Python_Mini_Project_Sem%20l/app/services/matching_service.py)  
**Notice:** This algorithm is strictly rule-based and deterministic. It does **not** rely on heuristic AI, black-box machine learning, or speculative statistical inference.

---

## 1. Engine Objective & Principles
The SkillConnect matching engine pairs students who have complementary educational needs:
1. **Reciprocal Priority:** A mutual exchange where Student A teaches Student B while Student B teaches Student A is given the highest priority.
2. **Deterministic & Transparent:** For any identical set of database records, the engine produces identical, reproducible results.
3. **Auditability:** Every recommendation is accompanied by the exact list of skills matched in both forward and reverse directions and an itemized score breakdown.
4. **Strict Bounds:** Compatibility percentages are bounded strictly between $0\%$ and $100\%$.
5. **Privacy & Hygiene:** The current student is excluded from their own results; candidates with zero complementary skills are omitted from recommendations.

---

## 2. Mathematical Formalization

### 2.1 Definitions & Notation
Let Student $A$ be the active logged-in student, and Student $B$ be a candidate student ($A \neq B$).
- $T_A$: The set of skills Student $A$ offers to teach (`skill_type = 'teach'`).
- $L_A$: The set of skills Student $A$ seeks to learn (`skill_type = 'learn'`).
- $T_B$: The set of skills Student $B$ offers to teach (`skill_type = 'teach'`).
- $L_B$: The set of skills Student $B$ seeks to learn (`skill_type = 'learn'`).

### 2.2 Directional Intersections
1. **Forward Match Set ($M_{\text{fwd}}$):** Skills Student $A$ wants to learn that Student $B$ offers to teach:
   $$M_{\text{fwd}} = L_A \cap T_B$$
2. **Reverse Match Set ($M_{\text{rev}}$):** Skills Student $A$ can teach that Student $B$ wants to learn:
   $$M_{\text{rev}} = T_A \cap L_B$$

### 2.3 Proficiency Mapping
Proficiency strings stored in `UserSkill.proficiency` are mapped to ordinal numeric weights:
$$\text{Weight}(p) = \begin{cases} 
1 & \text{if } p = \text{"beginner"} \\
2 & \text{if } p = \text{"intermediate"} \\
3 & \text{if } p = \text{"advanced"}
\end{cases}$$

For any matched skill, the teacher's proficiency level is compared against the learner's desired proficiency level:
$$\Delta_{\text{prof}} = \text{Weight}(\text{Teacher}) - \text{Weight}(\text{Learner})$$

When $\Delta_{\text{prof}} \ge 0$, the teacher possesses equal or higher mastery than the learner's current competence, ensuring high pedagogical value.

---

## 3. Compatibility Scoring Formula

If $|M_{\text{fwd}}| = 0$ and $|M_{\text{rev}}| = 0$:
$$\text{Score}(A, B) = 0 \quad (\text{Candidate has no complementary skills and is omitted from recommendations})$$

When at least one directional match exists, the compatibility score is calculated using the following deterministic formula (Maximum: **100 points**):

$$\text{Final Score} = \min\Big(100, \, \max\big(0, \, S_{\text{fwd}} + S_{\text{rev}} + S_{\text{cat}} + S_{\text{prof}}\big)\Big)$$

### Breakdown of Points:

| Component | Points | Prerequisite & Rule | Description |
| :--- | :---: | :--- | :--- |
| **Forward Match ($S_{\text{fwd}}$)** | **40 pts** | Awarded if and only if $\|M_{\text{fwd}}\| > 0$ | My LEARN skill matches Candidate's TEACH skill. Awarded once regardless of volume to avoid duplicate distortion. |
| **Reverse Match ($S_{\text{rev}}$)** | **40 pts** | Awarded if and only if $\|M_{\text{rev}}\| > 0$ | Candidate's LEARN skill matches My TEACH skill. Represents the reciprocal teaching obligation. |
| **Category Compatibility ($S_{\text{cat}}$)** | **10 pts** | Awarded if match is reciprocal OR matched skills belong to established categories | Aligned curriculum domains (e.g. Programming, Web Development, Database, Design). |
| **Proficiency Compatibility ($S_{\text{prof}}$)** | **10 pts** | Awarded if $\exists s: \Delta_{\text{prof}}(s) \ge 0$ | Teacher's proficiency meets or exceeds learner's target proficiency in at least one matched direction. |

### Classification:
1. **Reciprocal Match:** Both $S_{\text{fwd}} = 40$ and $S_{\text{rev}} = 40$ are awarded.
   $$\text{Score} \in [80, 100]$$
   - With category and proficiency bonuses satisfied: **100% compatibility**.
   - Identified in UI with a green `Reciprocal` badge.
2. **One-Way Match:** Either $S_{\text{fwd}} = 40$ or $S_{\text{rev}} = 40$, but not both.
   $$\text{Score} \in [40, 60]$$
   - Typically **50% to 60% compatibility** depending on category and proficiency alignment.
   - Identified in UI with a blue `One-Way` badge.

---

## 4. Deterministic Candidate Ranking & Tie-Breaking
When generating peer recommendations via `MatchingService.get_matches_for_user(current_user)`:
1. **Reciprocity Priority:** Reciprocal matches (`is_reciprocal == True`) are placed before one-way matches.
2. **Score Descending:** Highest compatibility score first ($100 \to 90 \to 80 \dots$).
3. **Total Matched Skills Count Descending:** Candidates offering more exchange options are ranked higher.
4. **Candidate ID Ascending:** Stable, deterministic tie-breaker ensuring zero non-deterministic jitter across page reloads.

```python
matches.sort(
    key=lambda m: (
        1 if m['is_reciprocal'] else 0,
        m['score'],
        m['fwd_count'] + m['rev_count'],
        -m['candidate'].id  # Negative ID for reverse sort = ascending ID order
    ),
    reverse=True
)
```

---

## 5. UI Representation and Audit Trail
In the matching recommendations page (`/matching/`):
- Each card displays the Candidate's Name, College, Bio, and Compatibility percentage badge.
- **Audit Explanation:** Displays the human-readable breakdown of awarded points:
  - `+40 pts: You learn Python from Jane Doe`
  - `+40 pts: Jane Doe learns UI/UX Design from you`
  - `+10 pts: Skill category alignment`
  - `+10 pts: Proficiency level compatibility (teacher meets/exceeds learner need)`
- **Skill Buckets:** Explicitly separates:
  - *"Skills Jane Doe can teach you"* (Forward matches)
  - *"Skills Jane Doe wants to learn from you"* (Reverse matches)
- **Profile View:** Direct link to inspect full student profile at `/matching/student/<id>`.
- **Exchange Request Button:** Marked as disabled with a badge `(Available in Phase 4)` to preserve workflow integrity without misleading interactive elements.
