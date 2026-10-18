"""
ExchangeRequest and ExchangeSession models for SkillConnect.
"""
from datetime import datetime, timezone
from app.extensions import db

class ExchangeRequest(db.Model):
    __tablename__ = 'exchange_requests'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    offered_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    requested_skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'accepted', 'rejected', 'cancelled'
    message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='sent_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='received_requests')
    offered_skill = db.relationship('Skill', foreign_keys=[offered_skill_id])
    requested_skill = db.relationship('Skill', foreign_keys=[requested_skill_id])
    session = db.relationship('ExchangeSession', back_populates='request', uselist=False, cascade='all, delete-orphan')

    @property
    def is_pending(self) -> bool:
        return self.status == 'pending'

    @property
    def is_accepted(self) -> bool:
        return self.status == 'accepted'

    @property
    def is_rejected(self) -> bool:
        return self.status == 'rejected'

    @property
    def is_cancelled(self) -> bool:
        return self.status == 'cancelled'

    @property
    def status_badge_class(self) -> str:
        mapping = {
            'pending': 'warning',
            'accepted': 'success',
            'rejected': 'danger',
            'cancelled': 'secondary'
        }
        return mapping.get(self.status, 'secondary')

    def partner(self, current_user_id: int):
        """Return the other participant in this exchange."""
        return self.receiver if self.sender_id == current_user_id else self.sender

    def is_participant(self, user_id: int) -> bool:
        return self.sender_id == user_id or self.receiver_id == user_id

    def __repr__(self) -> str:
        return f"<ExchangeRequest id={self.id} sender={self.sender_id} receiver={self.receiver_id} status='{self.status}'>"


class ExchangeSession(db.Model):
    __tablename__ = 'exchange_sessions'

    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey('exchange_requests.id'), unique=True, nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=60)
    mode = db.Column(db.String(20), nullable=False, default='online')  # 'online', 'in_person', 'hybrid'
    meeting_details = db.Column(db.String(255), nullable=True)  # URL or physical room
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='scheduled')  # 'scheduled', 'completed', 'cancelled'
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    request = db.relationship('ExchangeRequest', back_populates='session')
    ratings = db.relationship('Rating', back_populates='session', cascade='all, delete-orphan', lazy='selectin')

    @property
    def is_scheduled(self) -> bool:
        return self.status == 'scheduled'

    @property
    def is_completed(self) -> bool:
        return self.status == 'completed'

    @property
    def is_cancelled(self) -> bool:
        return self.status == 'cancelled'

    @property
    def status_badge_class(self) -> str:
        mapping = {
            'scheduled': 'primary',
            'completed': 'success',
            'cancelled': 'secondary'
        }
        return mapping.get(self.status, 'secondary')

    @property
    def formatted_date(self) -> str:
        return self.scheduled_at.strftime('%A, %b %d, %Y')

    @property
    def formatted_time(self) -> str:
        return self.scheduled_at.strftime('%I:%M %p')

    def is_participant(self, user_id: int) -> bool:
        """Check if user is a participant of the underlying exchange."""
        if not self.request:
            return False
        return self.request.sender_id == user_id or self.request.receiver_id == user_id

    def partner(self, current_user_id: int):
        """Return the other participant in this session."""
        if not self.request:
            return None
        return self.request.partner(current_user_id)

    def has_user_rated(self, user_id: int) -> bool:
        """Check if user has already submitted a rating for this session."""
        return any(r.reviewer_id == user_id for r in self.ratings)

    def get_user_rating(self, user_id: int):
        """Retrieve the rating submitted by a specific user for this session, if any."""
        for r in self.ratings:
            if r.reviewer_id == user_id:
                return r
        return None

    def get_partner_rating(self, current_user_id: int):
        """Retrieve the rating submitted by the session partner, if any."""
        for r in self.ratings:
            if r.reviewer_id != current_user_id:
                return r
        return None

    def __repr__(self) -> str:
        return f"<ExchangeSession id={self.id} request_id={self.request_id} status='{self.status}'>"
