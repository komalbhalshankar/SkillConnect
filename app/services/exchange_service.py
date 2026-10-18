"""
ExchangeService: Manages exchange requests, valid state transitions, session scheduling, and lifecycle.
"""
from datetime import datetime, timezone, timedelta
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
        Create a new skill exchange proposal.
        Enforces:
        1. sender != receiver
        2. valid existing student accounts
        3. offered skill belongs to sender's TEACH portfolio
        4. requested skill belongs to sender's LEARN portfolio
        5. requested skill belongs to receiver's TEACH portfolio
        6. offered skill belongs to receiver's LEARN portfolio (if receiver has a learn wishlist)
        7. no duplicate active pending or accepted request for identical pair and skills
        """
        if sender_id == receiver_id:
            return None, "You cannot send an exchange request to yourself."

        sender = db.session.get(User, sender_id)
        if not sender or sender.role != 'student':
            return None, "Sender student does not exist."

        receiver = db.session.get(User, receiver_id)
        if not receiver or receiver.role != 'student':
            return None, "Target student does not exist."

        offered = db.session.get(Skill, offered_skill_id)
        requested = db.session.get(Skill, requested_skill_id)
        if not offered or not requested:
            return None, "Offered and requested skills must be valid existing skills."

        # 3. Offered skill must belong to sender's TEACH portfolio
        sender_teach_ids = {us.skill_id for us in sender.teach_skills}
        if offered_skill_id not in sender_teach_ids:
            return None, f"You can only offer skills listed in your 'Teach' portfolio ({offered.name} is not listed)."

        # 4. Requested skill must belong to sender's LEARN portfolio
        sender_learn_ids = {us.skill_id for us in sender.learn_skills}
        if requested_skill_id not in sender_learn_ids:
            return None, f"You can only request skills listed in your 'Learn' portfolio ({requested.name} is not listed)."

        # 5. Requested skill must belong to receiver's TEACH portfolio
        receiver_teach_ids = {us.skill_id for us in receiver.teach_skills}
        if requested_skill_id not in receiver_teach_ids:
            return None, f"{receiver.name} does not offer to teach {requested.name}."

        # 6. Reciprocal alignment: If receiver has learn skills declared, offered skill should be in receiver's wishlist
        receiver_learn_ids = {us.skill_id for us in receiver.learn_skills}
        if receiver_learn_ids and offered_skill_id not in receiver_learn_ids:
            return None, f"{receiver.name} has not listed {offered.name} in their 'Learn' wishlist."

        # 7. Check for active duplicate request
        existing_pending = ExchangeRequest.query.filter_by(
            sender_id=sender_id,
            receiver_id=receiver_id,
            offered_skill_id=offered_skill_id,
            requested_skill_id=requested_skill_id,
            status='pending'
        ).first()

        if existing_pending:
            return None, "You already have a pending exchange request for these skills with this student."

        existing_accepted = ExchangeRequest.query.filter_by(
            sender_id=sender_id,
            receiver_id=receiver_id,
            offered_skill_id=offered_skill_id,
            requested_skill_id=requested_skill_id,
            status='accepted'
        ).first()

        if existing_accepted:
            return None, "An active accepted exchange agreement for these skills already exists with this student."

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
        Enforces:
        - participant authorization (sender or receiver)
        - request status must be 'accepted'
        - future datetime
        - valid duration (15 to 300 minutes)
        - rescheduling policy: if a session is already scheduled, reject;
          if cancelled, update the session to 'scheduled' with the new details.
        """
        req = db.session.get(ExchangeRequest, request_id)
        if not req:
            return None, "Exchange request not found."

        if not req.is_participant(user_id):
            return None, "Unauthorized: You are not a participant in this exchange."

        if req.status != 'accepted':
            return None, "A session can only be scheduled for an accepted exchange request."

        # Date validation: compare against now in UTC or naive local
        now_dt = datetime.now(timezone.utc) if scheduled_at.tzinfo else datetime.now()
        if scheduled_at < (now_dt - timedelta(minutes=5)):
            return None, "Session date and time cannot be in the past."

        if duration_minutes < 15 or duration_minutes > 300:
            return None, "Session duration must be between 15 and 300 minutes."

        clean_mode = mode.strip().lower()
        if clean_mode not in ['online', 'in_person', 'hybrid']:
            clean_mode = 'online'

        if req.session:
            if req.session.status == 'scheduled':
                return None, "A session is already scheduled for this exchange."
            elif req.session.status == 'completed':
                return None, "This exchange session has already been completed."
            elif req.session.status == 'cancelled':
                # Reschedule policy: update cancelled session
                sess = req.session
                sess.scheduled_at = scheduled_at
                sess.duration_minutes = duration_minutes
                sess.mode = clean_mode
                sess.meeting_details = meeting_details.strip() if meeting_details else None
                sess.notes = notes.strip() if notes else None
                sess.status = 'scheduled'
                db.session.commit()
                return sess, None

        session = ExchangeSession(
            request_id=req.id,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
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
        Only a participant can complete, and only if status is 'scheduled'.
        """
        sess = db.session.get(ExchangeSession, session_id)
        if not sess:
            return False, "Session not found."

        if not sess.is_participant(user_id):
            return False, "Unauthorized: You are not a participant in this session."

        if sess.status != 'scheduled':
            return False, f"Cannot complete a session with status '{sess.status}'."

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
        Only a participant can cancel, and only if status is 'scheduled'.
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
        Retrieve all requests involving the user, separated into incoming and outgoing.
        """
        incoming = ExchangeRequest.query.filter_by(receiver_id=user_id).order_by(ExchangeRequest.created_at.desc()).all()
        outgoing = ExchangeRequest.query.filter_by(sender_id=user_id).order_by(ExchangeRequest.created_at.desc()).all()
        return {
            'incoming': incoming,
            'outgoing': outgoing
        }

    @staticmethod
    def get_user_sessions(user_id: int) -> Dict[str, List[ExchangeSession]]:
        """
        Retrieve all sessions involving the user, separated into upcoming and past.
        """
        sessions = ExchangeSession.query.join(ExchangeRequest).filter(
            (ExchangeRequest.sender_id == user_id) | (ExchangeRequest.receiver_id == user_id)
        ).order_by(ExchangeSession.scheduled_at.asc()).all()

        upcoming = [s for s in sessions if s.status == 'scheduled']
        past = [s for s in sessions if s.status in ['completed', 'cancelled']]
        past.sort(key=lambda s: s.scheduled_at, reverse=True)

        return {
            'upcoming': upcoming,
            'past': past,
            'all': sessions
        }
