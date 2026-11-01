"""
Rating and Feedback model.
"""
from datetime import datetime, timezone
from app.extensions import db

class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('exchange_sessions.id'), nullable=False, index=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Constraints: One rating per reviewer per session
    __table_args__ = (
        db.UniqueConstraint('session_id', 'reviewer_id', name='uq_session_reviewer'),
        db.CheckConstraint('score >= 1 AND score <= 5', name='ck_rating_score_range'),
    )

    # Relationships
    session = db.relationship('ExchangeSession', back_populates='ratings')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], back_populates='given_ratings')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], back_populates='received_ratings')

    def __init__(
        self,
        session_id=None,
        reviewer_id=None,
        reviewee_id=None,
        score=None,
        feedback=None,
        **kwargs
    ):
        self.session_id = session_id
        self.reviewer_id = reviewer_id
        self.reviewee_id = reviewee_id
        self.score = score
        self.feedback = feedback
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return f"<Rating id={self.id} session={self.session_id} reviewer={self.reviewer_id} score={self.score}>"

