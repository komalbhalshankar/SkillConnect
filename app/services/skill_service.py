"""
SkillService: Handles catalog queries, skill portfolio CRUD,
custom skill creation without uncontrolled duplicates, and student discovery.
"""
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy import func
from app.extensions import db
from app.models.user import User
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
        skill_id: Optional[int] = None,
        skill_type: str = 'teach',
        proficiency: str = 'intermediate',
        notes: Optional[str] = None,
        custom_skill_name: Optional[str] = None,
        category_id: Optional[int] = None
    ) -> Tuple[Optional[UserSkill], Optional[str]]:
        """
        Add a skill to a student's portfolio.
        Supports selecting an existing skill or entering an unlisted custom skill safely.
        Enforces uniqueness: cannot add duplicate skill under the same skill_type.
        Permits having the same skill in both TEACH and LEARN.
        """
        clean_type = skill_type.strip().lower()
        if clean_type not in ['teach', 'learn']:
            return None, "Invalid skill type. Must be 'teach' or 'learn'."

        clean_prof = proficiency.strip().lower()
        if clean_prof not in ['beginner', 'intermediate', 'advanced']:
            clean_prof = 'intermediate'

        # Resolve the Skill entity
        target_skill = None

        # Check if a custom skill name is supplied
        if custom_skill_name and custom_skill_name.strip():
            clean_name = custom_skill_name.strip()
            # Case-insensitive check to reuse existing standard skill if it already exists
            existing_skill = Skill.query.filter(func.lower(Skill.name) == clean_name.lower()).first()
            if existing_skill:
                target_skill = existing_skill
            else:
                # Need a category
                cat = None
                if category_id:
                    cat = db.session.get(SkillCategory, category_id)
                if not cat:
                    # Fallback to 'Other' or the first available category
                    cat = SkillCategory.query.filter(func.lower(SkillCategory.name) == 'other').first()
                    if not cat:
                        cat = SkillCategory.query.first()
                    if not cat:
                        # Create an 'Other' category if none exists
                        cat = SkillCategory(name='Other', icon='bi-tags', description='General and miscellaneous skills.')
                        db.session.add(cat)
                        db.session.flush()

                target_skill = Skill(category_id=cat.id, name=clean_name.title())
                db.session.add(target_skill)
                db.session.flush()
        elif skill_id is not None and skill_id > 0:
            target_skill = db.session.get(Skill, skill_id)
            if not target_skill:
                return None, "Selected skill does not exist."
        else:
            return None, "Please select an existing skill or enter a new skill name."

        # Duplicate check: same user, same skill, same skill_type
        existing_user_skill = UserSkill.query.filter_by(
            user_id=user_id,
            skill_id=target_skill.id,
            skill_type=clean_type
        ).first()

        if existing_user_skill:
            return None, f"You already have '{target_skill.name}' in your {clean_type.upper()} skills list."

        user_skill = UserSkill(
            user_id=user_id,
            skill_id=target_skill.id,
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
        notes: Optional[str] = None,
        skill_type: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update skill type, proficiency, or notes of an existing user skill.
        Enforces ownership and prevents duplicate entries if changing skill type.
        """
        user_skill = db.session.get(UserSkill, user_skill_id)
        if not user_skill:
            return False, "Skill record not found."

        if user_skill.user_id != user_id:
            return False, "Unauthorized: You can only edit your own skills."

        clean_prof = proficiency.strip().lower()
        if clean_prof not in ['beginner', 'intermediate', 'advanced']:
            return False, "Invalid proficiency level."

        # If skill_type is being modified
        if skill_type:
            clean_type = skill_type.strip().lower()
            if clean_type not in ['teach', 'learn']:
                return False, "Invalid skill type."
            if clean_type != user_skill.skill_type:
                # Check for collision with an existing record of the target type
                collision = UserSkill.query.filter_by(
                    user_id=user_id,
                    skill_id=user_skill.skill_id,
                    skill_type=clean_type
                ).first()
                if collision:
                    return False, f"You already have '{user_skill.skill.name}' in your {clean_type.upper()} list."
                user_skill.skill_type = clean_type

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
    def search_students(
        current_user_id: int,
        query: Optional[str] = None,
        category_id: Optional[int] = None,
        proficiency: Optional[str] = None,
        intent: str = 'all'
    ) -> List[User]:
        """
        Search and filter peers in the database excluding the current logged-in student.
        """
        student_query = User.query.filter(User.role == 'student', User.id != current_user_id)

        # If any skill filters are applied, join with UserSkill and Skill
        if query or category_id or proficiency or intent in ['teach', 'learn']:
            student_query = student_query.join(User.user_skills).join(UserSkill.skill)

            if query and query.strip():
                clean_q = f"%{query.strip().lower()}%"
                student_query = student_query.filter(func.lower(Skill.name).like(clean_q))

            if category_id and category_id > 0:
                student_query = student_query.filter(Skill.category_id == category_id)

            if proficiency and proficiency.strip():
                student_query = student_query.filter(UserSkill.proficiency == proficiency.strip().lower())

            if intent in ['teach', 'learn']:
                student_query = student_query.filter(UserSkill.skill_type == intent)

            student_query = student_query.distinct()

        return student_query.order_by(User.name.asc()).all()

    @staticmethod
    def create_category(name: str, description: Optional[str] = None, icon: str = 'bi-tag') -> Tuple[Optional[SkillCategory], Optional[str]]:
        """Create a new skill category (Admin only)."""
        name_clean = name.strip()
        if not name_clean:
            return None, "Category name is required."

        if SkillCategory.query.filter(func.lower(SkillCategory.name) == name_clean.lower()).first():
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

        if Skill.query.filter(func.lower(Skill.name) == name_clean.lower()).first():
            return None, "Skill already exists."

        cat = db.session.get(SkillCategory, category_id)
        if not cat:
            return None, "Category not found."

        skill = Skill(category_id=category_id, name=name_clean, description=description)
        db.session.add(skill)
        db.session.commit()
        return skill, None
