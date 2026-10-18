"""
RatingService: Submits, validates, and computes peer exchange evaluations.
"""
from typing import Optional, Tuple, List
from app.extensions import db
from app.models.user import User
from app.models.exchange import ExchangeSession
from app.models.rating import Rating

class RatingService:

    @staticmethod
    def submit_rating(
        session_id: int,
        reviewer_id: int,
        score: int,
        feedback: Optional[str] = None
    ) -> Tuple[Optional[Rating], Optional[str]]:
        """
        Submit a post-session peer review.
        Enforces:
        - Session must exist and be in 'completed' status.
        - Reviewer must be a participant of the session.
        - Cannot submit duplicate rating for the same session.
        - Score must be between 1 and 5.
        """
        session = db.session.get(ExchangeSession, session_id)
        if not session:
            return None, "Session not found."

        if session.status != 'completed':
            return None, "You can only rate a session that has been marked as 'Completed'."

        if not session.is_participant(reviewer_id):
            return None, "Unauthorized: You were not a participant in this session."

        if session.has_user_rated(reviewer_id):
            return None, "You have already submitted a review for this session."

        if not isinstance(score, int) or score < 1 or score > 5:
            return None, "Rating score must be an integer between 1 and 5."

        # Determine reviewee: the other participant
        req = session.request
        reviewee_id = req.receiver_id if req.sender_id == reviewer_id else req.sender_id

        rating = Rating(
            session_id=session.id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            score=score,
            feedback=feedback.strip() if feedback else None
        )
        db.session.add(rating)
        db.session.commit()
        return rating, None

    @staticmethod
    def get_user_received_ratings(user_id: int) -> List[Rating]:
        return Rating.query.filter_by(reviewee_id=user_id).order_by(Rating.created_at.desc()).all()
