"""
AuthService: Business logic for registration, authentication, and profile updates.
"""
from typing import Optional, Tuple
from app.extensions import db
from app.models.user import User

class AuthService:

    @staticmethod
    def register_user(
        name: str,
        email: str,
        password: str,
        college: Optional[str] = None,
        bio: Optional[str] = None,
        availability: Optional[str] = None,
        role: str = 'student'
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user.
        Returns: (user, error_message)
        """
        clean_email = email.strip().lower()
        if not clean_email or '@' not in clean_email:
            return None, "A valid email address is required."

        if not name or len(name.strip()) < 2:
            return None, "Name must be at least 2 characters long."

        if not password or len(password) < 6:
            return None, "Password must be at least 6 characters long."

        existing_user = User.query.filter_by(email=clean_email).first()
        if existing_user:
            return None, "An account with this email address already exists."

        user = User(
            name=name.strip(),
            email=clean_email,
            role=role if role in ['student', 'admin'] else 'student',
            college=college.strip() if college else None,
            bio=bio.strip() if bio else None,
            availability=availability.strip() if availability else None
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[User]:
        """
        Verify credentials and return User if valid.
        """
        clean_email = email.strip().lower()
        user = User.query.filter_by(email=clean_email).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def update_profile(
        user: User,
        name: str,
        college: Optional[str] = None,
        bio: Optional[str] = None,
        availability: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Update user profile details.
        """
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long."

        user.name = name.strip()
        user.college = college.strip() if college else None
        user.bio = bio.strip() if bio else None
        user.availability = availability.strip() if availability else None

        db.session.commit()
        return True, None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        return db.session.get(User, user_id)
