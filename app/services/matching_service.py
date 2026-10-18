"""
MatchingService: Deterministic, rule-based two-way skill exchange matching engine.
Transparent, auditable, and strictly bounded between 0% and 100%.
"""
from typing import List, Dict, Any, Optional
from app.models.user import User
from app.models.skill import UserSkill

class MatchingService:

    @classmethod
    def calculate_compatibility(cls, user_a: User, user_b: User) -> Optional[Dict[str, Any]]:
        """
        Evaluate compatibility between Student A (current user) and Student B (candidate).
        Returns match dictionary or None if zero match exists.
        """
        if user_a.id == user_b.id:
            return None

        # Build skill lookups: skill_id -> UserSkill
        a_teach = {us.skill_id: us for us in user_a.user_skills if us.skill_type == 'teach'}
        a_learn = {us.skill_id: us for us in user_a.user_skills if us.skill_type == 'learn'}
        b_teach = {us.skill_id: us for us in user_b.user_skills if us.skill_type == 'teach'}
        b_learn = {us.skill_id: us for us in user_b.user_skills if us.skill_type == 'learn'}

        # Forward Matches: A wants to learn, B can teach
        fwd_ids = set(a_learn.keys()).intersection(set(b_teach.keys()))
        fwd_skills = []
        for sid in fwd_ids:
            learner_skill = a_learn[sid]
            teacher_skill = b_teach[sid]
            fwd_skills.append({
                'skill_id': sid,
                'skill_name': teacher_skill.skill.name,
                'category_name': teacher_skill.skill.category.name,
                'teacher_level': teacher_skill.proficiency,
                'learner_level': learner_skill.proficiency,
                'teacher_weight': teacher_skill.proficiency_weight,
                'learner_weight': learner_skill.proficiency_weight
            })

        # Reverse Matches: B wants to learn, A can teach
        rev_ids = set(a_teach.keys()).intersection(set(b_learn.keys()))
        rev_skills = []
        for sid in rev_ids:
            learner_skill = b_learn[sid]
            teacher_skill = a_teach[sid]
            rev_skills.append({
                'skill_id': sid,
                'skill_name': teacher_skill.skill.name,
                'category_name': teacher_skill.skill.category.name,
                'teacher_level': teacher_skill.proficiency,
                'learner_level': learner_skill.proficiency,
                'teacher_weight': teacher_skill.proficiency_weight,
                'learner_weight': learner_skill.proficiency_weight
            })

        # If zero matches in both directions, return None
        if not fwd_skills and not rev_skills:
            return None

        is_reciprocal = len(fwd_skills) > 0 and len(rev_skills) > 0

        if is_reciprocal:
            # Reciprocal Match Scoring
            base_score = 60
            # Volume bonus: up to 20 points
            total_matched_count = len(fwd_skills) + len(rev_skills)
            volume_bonus = min(20, max(0, (total_matched_count - 2) * 5))

            # Proficiency alignment: up to 10 points
            prof_bonus = 0
            if any(f['teacher_weight'] >= f['learner_weight'] for f in fwd_skills):
                prof_bonus += 5
            if any(r['teacher_weight'] >= r['learner_weight'] for r in rev_skills):
                prof_bonus += 5

            # Category synergy bonus: up to 10 points
            categories_fwd = {f['category_name'] for f in fwd_skills}
            categories_rev = {r['category_name'] for r in rev_skills}
            cat_bonus = 10 if len(categories_fwd.union(categories_rev)) >= 2 else 5

            raw_score = base_score + volume_bonus + prof_bonus + cat_bonus
            final_score = min(100, max(60, raw_score))
            match_type = 'Reciprocal'
            badge_class = 'success'
        else:
            # One-Way Match Scoring
            base_score = 30
            active_skills = fwd_skills if fwd_skills else rev_skills
            volume_bonus = min(15, (len(active_skills) - 1) * 5)
            
            # Proficiency bonus for teacher competence
            max_teacher_level = max(s['teacher_weight'] for s in active_skills)
            prof_bonus = 10 if max_teacher_level >= 3 else (5 if max_teacher_level >= 2 else 0)

            raw_score = base_score + volume_bonus + prof_bonus
            final_score = min(55, max(30, raw_score))
            match_type = 'One-Way'
            badge_class = 'info'

        return {
            'candidate': user_b,
            'score': final_score,
            'is_reciprocal': is_reciprocal,
            'match_type': match_type,
            'badge_class': badge_class,
            'fwd_skills': fwd_skills,  # Candidate teaches, Current user learns
            'rev_skills': rev_skills,  # Current user teaches, Candidate learns
            'fwd_count': len(fwd_skills),
            'rev_count': len(rev_skills)
        }

    @classmethod
    def get_matches_for_user(cls, user: User, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Find all compatible peer matches for the specified student.
        Sorted by Score (desc), Reciprocal first, Average Rating (desc), Name (asc).
        """
        # Fetch candidate students excluding the current user
        candidates = User.query.filter(User.role == 'student', User.id != user.id).all()
        matches = []

        for candidate in candidates:
            match_data = cls.calculate_compatibility(user, candidate)
            if match_data:
                matches.append(match_data)

        # Sorting logic:
        # 1. Score descending
        # 2. is_reciprocal True first
        # 3. Average rating descending
        # 4. Name ascending
        matches.sort(
            key=lambda m: (
                m['score'],
                1 if m['is_reciprocal'] else 0,
                m['candidate'].average_rating,
                -ord(m['candidate'].name[0].lower()) if m['candidate'].name else 0
            ),
            reverse=True
        )

        if limit:
            return matches[:limit]
        return matches
