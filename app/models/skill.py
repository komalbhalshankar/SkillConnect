"""
SkillCategory, Skill, and UserSkill relational models.
"""
from datetime import datetime, timezone
from app.extensions import db

class SkillCategory(db.Model):
    __tablename__ = 'skill_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(50), nullable=False, default='bi-tag')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    skills = db.relationship('Skill', back_populates='category', cascade='all, delete-orphan', lazy='selectin')

    def __repr__(self) -> str:
        return f"<SkillCategory id={self.id} name='{self.name}'>"

class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('skill_categories.id'), nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    category = db.relationship('SkillCategory', back_populates='skills')
    user_skills = db.relationship('UserSkill', back_populates='skill', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name='{self.name}'>"

class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False, index=True)
    skill_type = db.Column(db.String(10), nullable=False)  # 'teach' or 'learn'
    proficiency = db.Column(db.String(20), nullable=False, default='intermediate')  # 'beginner', 'intermediate', 'advanced'
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Constraints: A user cannot add the same skill twice for the same skill_type
    __table_args__ = (
        db.UniqueConstraint('user_id', 'skill_id', 'skill_type', name='uq_user_skill_type'),
    )

    # Relationships
    user = db.relationship('User', back_populates='user_skills')
    skill = db.relationship('Skill', back_populates='user_skills', lazy='joined')

    @property
    def proficiency_weight(self) -> int:
        """Map text proficiency to numeric weight for comparison."""
        mapping = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        return mapping.get(self.proficiency.lower(), 2)

    def __repr__(self) -> str:
        return f"<UserSkill id={self.id} user_id={self.user_id} skill_id={self.skill_id} type='{self.skill_type}' prof='{self.proficiency}'>"
