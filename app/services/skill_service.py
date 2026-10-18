"""
SkillService: Handles catalog queries, skill portfolio CRUD, and ownership validation.
"""
from typing import List, Optional, Tuple
from app.extensions import db
from app.models.skill import Skill, SkillCategory, UserSkill

class SkillService:

    @staticmethod
    def get_all_categories() -> List[SkillCategory]:
        return SkillCategory.query.order_by(SkillCategory.name.asc()).all()

    @staticmethod
    def get_all_skills() -> List[Skill]:
        return Skill.query.order_by(Skill.name.asc()).all()

    @staticmethod
    def get_skills_by_category(category_id: int) -> List[Skill]:
        return Skill.query.filter_by(category_id=category_id).order_by(Skill.name.asc()).all()

    @staticmethod
    def get_user_skills(user_id: int, skill_type: Optional[str] = None) -> List[UserSkill]:
        query = UserSkill.query.filter_by(user_id=user_id)
        if skill_type:
            query = query.filter_by(skill_type=skill_type.lower())
        return query.all()

    @staticmethod
    def add_user_skill(
        user_id: int,
        skill_id: int,
        skill_type: str,
        proficiency: str = 'intermediate',
        notes: Optional[str] = None
    ) -> Tuple[Optional[UserSkill], Optional[str]]:
        """
        Add a skill to a student's portfolio.
        Enforces uniqueness: cannot add duplicate skill under the same type.
        """
        clean_type = skill_type.strip().lower()
        if clean_type not in ['teach', 'learn']:
            return None, "Invalid skill type. Must be 'teach' or 'learn'."

        clean_prof = proficiency.strip().lower()
        if clean_prof not in ['beginner', 'intermediate', 'advanced']:
            clean_prof = 'intermediate'

        skill = db.session.get(Skill, skill_id)
        if not skill:
            return None, "Selected skill does not exist."

        existing = UserSkill.query.filter_by(
            user_id=user_id,
            skill_id=skill_id,
            skill_type=clean_type
        ).first()

        if existing:
            return None, f"You already have '{skill.name}' in your {clean_type} skills list."

        opposite_type = 'learn' if clean_type == 'teach' else 'teach'
        opposite_existing = UserSkill.query.filter_by(
            user_id=user_id,
            skill_id=skill_id,
            skill_type=opposite_type
        ).first()

        if opposite_existing:
            return None, f"You are already registered to {opposite_type} '{skill.name}'. A skill cannot be added to both Teach and Learn simultaneously."

        user_skill = UserSkill(
            user_id=user_id,
            skill_id=skill_id,
            skill_type=clean_type,
            proficiency=clean_prof,
            notes=notes.strip() if notes else None
        )
        db.session.add(user_skill)
        db.session.commit()
        return user_skill, None

    @staticmethod
    def update_user_skill(
        user_skill_id: int,
        user_id: int,
        proficiency: str,
        notes: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update proficiency or notes of an existing user skill.
        Enforces ownership.
        """
        user_skill = db.session.get(UserSkill, user_skill_id)
        if not user_skill:
            return False, "Skill record not found."

        if user_skill.user_id != user_id:
            return False, "Unauthorized: You can only edit your own skills."

        clean_prof = proficiency.strip().lower()
        if clean_prof not in ['beginner', 'intermediate', 'advanced']:
            return False, "Invalid proficiency level."

        user_skill.proficiency = clean_prof
        user_skill.notes = notes.strip() if notes else None
        db.session.commit()
        return True, None

    @staticmethod
    def delete_user_skill(user_skill_id: int, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a skill from a student's portfolio.
        Enforces ownership.
        """
        user_skill = db.session.get(UserSkill, user_skill_id)
        if not user_skill:
            return False, "Skill record not found."

        if user_skill.user_id != user_id:
            return False, "Unauthorized: You can only delete your own skills."

        db.session.delete(user_skill)
        db.session.commit()
        return True, None

    @staticmethod
    def create_category(name: str, description: Optional[str] = None, icon: str = 'bi-tag') -> Tuple[Optional[SkillCategory], Optional[str]]:
        """Create a new skill category (Admin only)."""
        name_clean = name.strip()
        if not name_clean:
            return None, "Category name is required."

        if SkillCategory.query.filter_by(name=name_clean).first():
            return None, "Category already exists."

        cat = SkillCategory(name=name_clean, description=description, icon=icon or 'bi-tag')
        db.session.add(cat)
        db.session.commit()
        return cat, None

    @staticmethod
    def create_skill(category_id: int, name: str, description: Optional[str] = None) -> Tuple[Optional[Skill], Optional[str]]:
        """Create a new standardized skill (Admin only)."""
        name_clean = name.strip()
        if not name_clean:
            return None, "Skill name is required."

        if Skill.query.filter_by(name=name_clean).first():
            return None, "Skill already exists."

        cat = db.session.get(SkillCategory, category_id)
        if not cat:
            return None, "Category not found."

        skill = Skill(category_id=category_id, name=name_clean, description=description)
        db.session.add(skill)
        db.session.commit()
        return skill, None
