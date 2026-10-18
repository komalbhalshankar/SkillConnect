"""
RatingService: Submits, validates, and computes peer exchange evaluations.
"""
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.exc import IntegrityError
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
        - Cannot rate yourself.
        - Cannot submit duplicate rating for the same session.
        - Score must be an integer between 1 and 5.
        - Feedback comment must not exceed 500 characters.
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

        clean_feedback = feedback.strip() if feedback else None
        if clean_feedback and len(clean_feedback) > 500:
            return None, "Feedback must be 500 characters or fewer."

        # Determine reviewee: the other participant
        req = session.request
        if not req:
            return None, "Exchange request associated with session not found."

        reviewee_id = req.receiver_id if req.sender_id == reviewer_id else req.sender_id

        if reviewee_id == reviewer_id:
            return None, "You cannot rate yourself."

        rating = Rating(
            session_id=session.id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            score=score,
            feedback=clean_feedback
        )

        try:
            db.session.add(rating)
            db.session.commit()
            return rating, None
        except IntegrityError:
            db.session.rollback()
            return None, "You have already submitted a review for this session."
        except Exception as e:
            db.session.rollback()
            return None, f"Failed to submit rating: {str(e)}"

    @staticmethod
    def get_user_received_ratings(user_id: int) -> List[Rating]:
        """Fetch all peer ratings received by a student in descending chronological order."""
        return Rating.query.filter_by(reviewee_id=user_id).order_by(Rating.created_at.desc()).all()

    @staticmethod
    def get_session_rating_by_reviewer(session_id: int, reviewer_id: int) -> Optional[Rating]:
        """Retrieve rating submitted for a specific session by a reviewer."""
        return Rating.query.filter_by(session_id=session_id, reviewer_id=reviewer_id).first()

    @staticmethod
    def get_user_ratings_summary(user_id: int) -> Dict[str, Any]:
        """
        Compute rating statistics, average score, review count, and star distribution.
        """
        ratings = RatingService.get_user_received_ratings(user_id)
        count = len(ratings)
        avg = round(sum(r.score for r in ratings) / count, 1) if count > 0 else 0.0

        distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for r in ratings:
            if r.score in distribution:
                distribution[r.score] += 1

        return {
            'ratings': ratings,
            'review_count': count,
            'average_rating': avg,
            'distribution': distribution
        }
