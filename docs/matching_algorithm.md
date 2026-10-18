# SkillConnect — Deterministic Two-Way Skill Matching Engine Specification
**Version:** 1.0  
**Methodology:** Deterministic, Rule-Based Bilateral Compatibility Engine  
**Notice:** This algorithm is strictly rule-based and deterministic. It does **not** rely on heuristic AI, black-box machine learning, or speculative statistical inference.

---

## 1. Engine Objective & Principles
The SkillConnect matching engine pairs students who have complementary educational needs:
1. **Reciprocal Priority:** A mutual exchange where Student A teaches Student B while Student B teaches Student A is given the highest priority.
2. **Deterministic & Transparent:** For any identical set of database records, the engine produces identical, reproducible results.
3. **Auditability:** Every recommendation is accompanied by the exact list of skills matched in both forward and reverse directions.
4. **Strict Bounds:** Compatibility percentages are bounded strictly between $0\%$ and $100\%$.
5. **Privacy & Hygiene:** The current student is excluded from their own results; candidates with zero matching skills are omitted.

---

## 2. Mathematical Formalization

### 2.1 Definitions & Notation
Let Student $A$ be the active logged-in student, and Student $B$ be a candidate student ($A \neq B$).
- $T_A$: The set of skills Student $A$ offers to teach (`Teach`).
- $L_A$: The set of skills Student $A$ seeks to learn (`Learn`).
- $T_B$: The set of skills Student $B$ offers to teach (`Teach`).
- $L_B$: The set of skills Student $B$ seeks to learn (`Learn`).

### 2.2 Directional Intersections
1. **Forward Match Set ($M_{\text{fwd}}$):** Skills Student $A$ wants to learn that Student $B$ is able to teach:
   $$M_{\text{fwd}} = L_A \cap T_B$$
2. **Reverse Match Set ($M_{\text{rev}}$):** Skills Student $A$ can teach that Student $B$ wants to learn:
   $$M_{\text{rev}} = T_A \cap L_B$$

### 2.3 Proficiency Mapping
Proficiency strings are mapped to ordinal numeric weights:
$$\text{Level}(p) = \begin{cases} 
1 & \text{if } p = \text{"Beginner"} \\
2 & \text{if } p = \text{"Intermediate"} \\
3 & \text{if } p = \text{"Advanced"}
\end{cases}$$

For any matched skill $s \in M_{\text{fwd}}$, Student $B$ is the teacher and Student $A$ is the learner:
$$\Delta_{\text{prof}}(s) = \text{Level}(\text{Teacher}) - \text{Level}(\text{Learner})$$

A non-negative delta ($\Delta_{\text{prof}} \ge 0$) indicates optimal learning suitability (the instructor is at or above the learner's current competence).

---

## 3. Compatibility Scoring Formula

If $|M_{\text{fwd}}| = 0$ and $|M_{\text{rev}}| = 0$:
$$\text{Score}(A, B) = 0\% \quad (\text{Candidate is omitted from recommendations})$$

### Case 1: Reciprocal (Two-Way) Synergy ($|M_{\text{fwd}}| > 0$ and $|M_{\text{rev}}| > 0$)
When both students can teach each other at least one desired skill, the match is designated **Reciprocal**:
$$\text{Score}_{\text{reciprocal}} = S_{\text{base}} + S_{\text{volume}} + S_{\text{prof}} + S_{\text{cat}}$$

Where:
1. **Base Reciprocal Score ($S_{\text{base}}$):** $60$ points.
2. **Skill Volume Bonus ($S_{\text{volume}}$):** 
   $$S_{\text{volume}} = \min\Big(20, \, (|M_{\text{fwd}}| + |M_{\text{rev}}| - 2) \times 5\Big)$$
   Rewarding students with multi-skill exchange opportunities.
3. **Proficiency Alignment ($S_{\text{prof}}$):**
   Up to $10$ points: $+5$ points if the forward teacher proficiency $\ge$ learner proficiency, and $+5$ points if the reverse teacher proficiency $\ge$ learner proficiency.
4. **Category Synergy ($S_{\text{cat}}$):**
   Up to $10$ points if the skills span diverse academic categories.

$$\text{Final Score} = \min(100, \, \max(60, \, \text{Score}_{\text{reciprocal}}))$$

### Case 2: One-Way (Complementary) Synergy ($|M_{\text{fwd}}| > 0 \oplus |M_{\text{rev}}| > 0$)
When only one direction has an intersection, the match is designated **One-Way**:
$$\text{Score}_{\text{oneway}} = 30 + \min(15, (|M_{\text{matched}}| - 1) \times 5) + S_{\text{prof}}$$
Where:
- $S_{\text{prof}} \in \{0, 5, 10\}$ based on whether the teacher's proficiency is Intermediate ($+5$) or Advanced ($+10$).
$$\text{Final Score} = \min(55, \, \max(30, \, \text{Score}_{\text{oneway}}))$$

---

## 4. Score Stratification & Interpretability
| Score Range | Classification | Meaning | UI Badge |
| :---: | :---: | :--- | :---: |
| **85% – 100%** | Exceptional Bilateral | Mutual multi-skill exchange with verified proficiency advantage | <span style="color:green">**Excellent Reciprocal**</span> |
| **60% – 84%** | Strong Bilateral | Direct two-way exchange (both can teach what the other needs) | <span style="color:blue">**Reciprocal Match**</span> |
| **40% – 55%** | Favorable One-Way | One student has an exact skill desired with strong proficiency | <span style="color:orange">**One-Way Match**</span> |
| **30% – 39%** | Basic One-Way | Single beginner-level one-way skill match | <span style="color:gray">**Partial Match**</span> |
| **0%** | No Match | Zero skill overlap; candidate filtered out | *Hidden* |

---

## 5. Candidate Ranking & Tie-Breaking
Recommended partners are sorted according to:
1. **Compatibility Score** (Descending)
2. **Reciprocal Match Flag** (Reciprocal before One-Way)
3. **Average Star Rating** (Descending)
4. **Alphabetical Name** (Ascending deterministic tie-breaker)
