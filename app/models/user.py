"""
User model representing Students and Administrators.
"""
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(180), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    college = db.Column(db.String(180), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    availability = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    user_skills = db.relationship('UserSkill', back_populates='user', cascade='all, delete-orphan', lazy='selectin')
    sent_requests = db.relationship(
        'ExchangeRequest',
        foreign_keys='ExchangeRequest.sender_id',
        back_populates='sender',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    received_requests = db.relationship(
        'ExchangeRequest',
        foreign_keys='ExchangeRequest.receiver_id',
        back_populates='receiver',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    given_ratings = db.relationship(
        'Rating',
        foreign_keys='Rating.reviewer_id',
        back_populates='reviewer',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )
    received_ratings = db.relationship(
        'Rating',
        foreign_keys='Rating.reviewee_id',
        back_populates='reviewee',
        cascade='all, delete-orphan',
        lazy='dynamic'
    )

    def set_password(self, password: str) -> None:
        """Hash and store password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify hashed password."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        """Check if user has admin privileges."""
        return self.role == 'admin'

    @property
    def teach_skills(self):
        """List of skills the user can teach."""
        return [us for us in self.user_skills if us.skill_type == 'teach']

    @property
    def learn_skills(self):
        """List of skills the user wants to learn."""
        return [us for us in self.user_skills if us.skill_type == 'learn']

    @property
    def average_rating(self) -> float:
        """Compute the user's average rating as a float rounded to 1 decimal place."""
        ratings = list(self.received_ratings)
        if not ratings:
            return 0.0
        return round(sum(r.score for r in ratings) / len(ratings), 1)

    @property
    def review_count(self) -> int:
        """Count total reviews received."""
        return self.received_ratings.count()

    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}' role='{self.role}'>"

@login_manager.user_loader
def load_user(user_id: str):
    """Flask-Login user loader callback."""
    if user_id is not None:
        return db.session.get(User, int(user_id))
    return None
