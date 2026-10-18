"""
MatchingService: Rule-based reciprocal matching engine for SkillConnect.
Calculates transparent compatibility scores (0–100%) and returns detailed breakdowns.
"""
from typing import List, Dict, Any, Optional
from app.models.user import User
from app.models.skill import UserSkill

class MatchingService:

    @classmethod
    def calculate_compatibility(cls, user_a: User, user_b: User) -> Optional[Dict[str, Any]]:
        """
        Evaluate compatibility between Student A (current user) and Student B (candidate).
        Returns match dictionary or None if zero complementary skills exist.
        
        Formula (Max: 100 points):
        - 40 points: My LEARN skill matches Candidate's TEACH skill.
        - 40 points: Candidate's LEARN skill matches My TEACH skill.
        - 10 points: Category alignment compatibility bonus.
        - 10 points: Proficiency level compatibility bonus (Teacher level >= Learner level).
        """
        if user_a.id == user_b.id:
            return None

        # Build lookups: skill_id -> list of UserSkill
        a_teach = {us.skill_id: us for us in user_a.user_skills if us.skill_type == 'teach'}
        a_learn = {us.skill_id: us for us in user_a.user_skills if us.skill_type == 'learn'}
        b_teach = {us.skill_id: us for us in user_b.user_skills if us.skill_type == 'teach'}
        b_learn = {us.skill_id: us for us in user_b.user_skills if us.skill_type == 'learn'}

        # Forward matches (Direction 1: User A learns, Candidate B teaches)
        fwd_ids = set(a_learn.keys()).intersection(set(b_teach.keys()))
        fwd_skills = []
        for sid in sorted(fwd_ids):
            learner_skill = a_learn[sid]
            teacher_skill = b_teach[sid]
            fwd_skills.append({
                'skill_id': sid,
                'skill_name': teacher_skill.skill.name,
                'category_id': teacher_skill.skill.category_id,
                'category_name': teacher_skill.skill.category.name,
                'teacher_level': teacher_skill.proficiency,
                'learner_level': learner_skill.proficiency,
                'teacher_weight': teacher_skill.proficiency_weight,
                'learner_weight': learner_skill.proficiency_weight
            })

        # Reverse matches (Direction 2: User A teaches, Candidate B learns)
        rev_ids = set(a_teach.keys()).intersection(set(b_learn.keys()))
        rev_skills = []
        for sid in sorted(rev_ids):
            learner_skill = b_learn[sid]
            teacher_skill = a_teach[sid]
            rev_skills.append({
                'skill_id': sid,
                'skill_name': teacher_skill.skill.name,
                'category_id': teacher_skill.skill.category_id,
                'category_name': teacher_skill.skill.category.name,
                'teacher_level': teacher_skill.proficiency,
                'learner_level': learner_skill.proficiency,
                'teacher_weight': teacher_skill.proficiency_weight,
                'learner_weight': learner_skill.proficiency_weight
            })

        # If zero matches in both directions, exclude candidate from match recommendations
        if not fwd_skills and not rev_skills:
            return None

        has_fwd = len(fwd_skills) > 0
        has_rev = len(rev_skills) > 0
        is_reciprocal = has_fwd and has_rev

        score = 0
        score_breakdown = []

        # 1. Directional Points (40 pts each)
        if has_fwd:
            score += 40
            fwd_names = ", ".join(s['skill_name'] for s in fwd_skills)
            score_breakdown.append(f"+40 pts: You learn {fwd_names} from {user_b.name}")

        if has_rev:
            score += 40
            rev_names = ", ".join(s['skill_name'] for s in rev_skills)
            score_breakdown.append(f"+40 pts: {user_b.name} learns {rev_names} from you")

        # 2. Category Compatibility Bonus (10 pts)
        # Awarded when matched skills span aligned/shared categories
        fwd_cats = {s['category_id'] for s in fwd_skills}
        rev_cats = {s['category_id'] for s in rev_skills}
        # If reciprocal, or if matched skills belong to established categories
        if is_reciprocal or (fwd_cats or rev_cats):
            score += 10
            score_breakdown.append("+10 pts: Skill category alignment")

        # 3. Proficiency Compatibility Bonus (10 pts)
        # Awarded if teacher's proficiency meets or exceeds learner's target proficiency
        prof_compatible = False
        if any(f['teacher_weight'] >= f['learner_weight'] for f in fwd_skills):
            prof_compatible = True
        elif any(r['teacher_weight'] >= r['learner_weight'] for r in rev_skills):
            prof_compatible = True

        if prof_compatible:
            score += 10
            score_breakdown.append("+10 pts: Proficiency level compatibility (teacher meets/exceeds learner need)")

        # Ensure strict bounds [0, 100]
        final_score = min(100, max(0, score))

        match_type = 'Reciprocal' if is_reciprocal else 'One-Way'
        badge_class = 'success' if is_reciprocal else 'primary'

        return {
            'candidate': user_b,
            'score': final_score,
            'is_reciprocal': is_reciprocal,
            'match_type': match_type,
            'badge_class': badge_class,
            'fwd_skills': fwd_skills,  # Candidate teaches, Current user learns
            'rev_skills': rev_skills,  # Current user teaches, Candidate learns
            'fwd_count': len(fwd_skills),
            'rev_count': len(rev_skills),
            'score_breakdown': score_breakdown
        }

    @classmethod
    def get_matches_for_user(cls, user: User, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find all compatible peer matches for the specified student.
        Ranked deterministically:
        1. Reciprocal matches preferred (is_reciprocal True before False)
        2. Score descending
        3. Total matched skills count descending
        4. Candidate ID ascending (stable deterministic tie-breaker)
        """
        candidates = User.query.filter(User.role == 'student', User.id != user.id).all()
        matches = []

        for candidate in candidates:
            match_data = cls.calculate_compatibility(user, candidate)
            if match_data:
                matches.append(match_data)

        # Deterministic ranking
        matches.sort(
            key=lambda m: (
                1 if m['is_reciprocal'] else 0,
                m['score'],
                m['fwd_count'] + m['rev_count'],
                -m['candidate'].id
            ),
            reverse=True
        )

        if limit:
            return matches[:limit]
        return matches
