"""
ExchangeService: Manages exchange requests, valid state transitions, session scheduling, and lifecycle.
"""
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill
from app.models.exchange import ExchangeRequest, ExchangeSession

class ExchangeService:

    @staticmethod
    def create_request(
        sender_id: int,
        receiver_id: int,
        offered_skill_id: int,
        requested_skill_id: int,
        message: Optional[str] = None
    ) -> Tuple[Optional[ExchangeRequest], Optional[str]]:
        """
        Create a new exchange proposal.
        Enforces: sender != receiver, valid skills, no active duplicate pending requests.
        """
        if sender_id == receiver_id:
            return None, "You cannot send an exchange request to yourself."

        receiver = db.session.get(User, receiver_id)
        if not receiver or receiver.role != 'student':
            return None, "Target student does not exist."

        offered = db.session.get(Skill, offered_skill_id)
        requested = db.session.get(Skill, requested_skill_id)
        if not offered or not requested:
            return None, "Offered and requested skills must be valid existing skills."

        # Check for active duplicate request
        existing_active = ExchangeRequest.query.filter_by(
            sender_id=sender_id,
            receiver_id=receiver_id,
            offered_skill_id=offered_skill_id,
            requested_skill_id=requested_skill_id,
            status='pending'
        ).first()

        if existing_active:
            return None, "You already have a pending exchange request for these skills with this student."

        req = ExchangeRequest(
            sender_id=sender_id,
            receiver_id=receiver_id,
            offered_skill_id=offered_skill_id,
            requested_skill_id=requested_skill_id,
            message=message.strip() if message else None,
            status='pending'
        )
        db.session.add(req)
        db.session.commit()
        return req, None

    @staticmethod
    def respond_to_request(
        request_id: int,
        user_id: int,
        action: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Accept or reject an incoming request.
        Only the recipient can respond, and only if status is 'pending'.
        """
        req = db.session.get(ExchangeRequest, request_id)
        if not req:
            return False, "Exchange request not found."

        if req.receiver_id != user_id:
            return False, "Unauthorized: Only the recipient can accept or reject this request."

        if req.status != 'pending':
            return False, f"Cannot change request with status '{req.status}'."

        clean_action = action.strip().lower()
        if clean_action == 'accept':
            req.status = 'accepted'
        elif clean_action == 'reject':
            req.status = 'rejected'
        else:
            return False, "Invalid action. Must be 'accept' or 'reject'."

        db.session.commit()
        return True, None

    @staticmethod
    def cancel_request(
        request_id: int,
        user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Cancel an outgoing request.
        Only the sender can cancel, and only while status is 'pending'.
        """
        req = db.session.get(ExchangeRequest, request_id)
        if not req:
            return False, "Exchange request not found."

        if req.sender_id != user_id:
            return False, "Unauthorized: Only the sender can cancel this request."

        if req.status != 'pending':
            return False, f"Cannot cancel request with status '{req.status}'."

        req.status = 'cancelled'
        db.session.commit()
        return True, None

    @staticmethod
    def schedule_session(
        request_id: int,
        user_id: int,
        scheduled_at: datetime,
        duration_minutes: int = 60,
        mode: str = 'online',
        meeting_details: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Tuple[Optional[ExchangeSession], Optional[str]]:
        """
        Schedule a session for an accepted request.
        """
        req = db.session.get(ExchangeRequest, request_id)
        if not req:
            return None, "Exchange request not found."

        if req.sender_id != user_id and req.receiver_id != user_id:
            return None, "Unauthorized: You are not a participant in this exchange."

        if req.status != 'accepted':
            return None, "A session can only be scheduled for an accepted exchange request."

        if req.session:
            return None, "A session has already been scheduled for this exchange."

        clean_mode = mode.strip().lower()
        if clean_mode not in ['online', 'in_person', 'hybrid']:
            clean_mode = 'online'

        session = ExchangeSession(
            request_id=req.id,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes if duration_minutes > 0 else 60,
            mode=clean_mode,
            meeting_details=meeting_details.strip() if meeting_details else None,
            notes=notes.strip() if notes else None,
            status='scheduled'
        )
        db.session.add(session)
        db.session.commit()
        return session, None

    @staticmethod
    def complete_session(
        session_id: int,
        user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Mark a scheduled session as completed.
        """
        sess = db.session.get(ExchangeSession, session_id)
        if not sess:
            return False, "Session not found."

        if not sess.is_participant(user_id):
            return False, "Unauthorized: You are not a participant in this session."

        if sess.status != 'scheduled':
            return False, f"Cannot complete a session that is already '{sess.status}'."

        sess.status = 'completed'
        db.session.commit()
        return True, None

    @staticmethod
    def cancel_session(
        session_id: int,
        user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Cancel a scheduled session.
        """
        sess = db.session.get(ExchangeSession, session_id)
        if not sess:
            return False, "Session not found."

        if not sess.is_participant(user_id):
            return False, "Unauthorized: You are not a participant in this session."

        if sess.status != 'scheduled':
            return False, f"Cannot cancel a session that is '{sess.status}'."

        sess.status = 'cancelled'
        db.session.commit()
        return True, None

    @staticmethod
    def get_user_requests(user_id: int) -> Dict[str, List[ExchangeRequest]]:
        """
        Retrieve all requests involving the user, grouped by incoming and outgoing.
        """
        incoming = ExchangeRequest.query.filter_by(receiver_id=user_id).order_by(ExchangeRequest.created_at.desc()).all()
        outgoing = ExchangeRequest.query.filter_by(sender_id=user_id).order_by(ExchangeRequest.created_at.desc()).all()
        return {
            'incoming': incoming,
            'outgoing': outgoing
        }
