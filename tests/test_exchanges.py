"""
Unit and Integration tests for Module 4: Skill Exchange and Session Management.
All tests run against an isolated in-memory SQLite database.
"""
from datetime import datetime, timezone, timedelta, date, time
import pytest
from app.extensions import db
from app.models.user import User
from app.models.skill import Skill, SkillCategory, UserSkill
from app.models.exchange import ExchangeRequest, ExchangeSession
from app.services.exchange_service import ExchangeService
from app.services.skill_service import SkillService

@pytest.fixture
def setup_exchange_environment(app, student_user, second_student_user):
    """
    Sets up two students with complementary skills:
    - Student A (Aarav): Teaches Python (Advanced), Learns UI/UX Design (Beginner)
    - Student B (Priya): Teaches UI/UX Design (Advanced), Learns Python (Intermediate)
    """
    cat_prog = SkillCategory(name="Programming", icon="bi-code", description="Software dev")
    cat_design = SkillCategory(name="Design", icon="bi-palette", description="UI/UX")
    db.session.add_all([cat_prog, cat_design])
    db.session.commit()

    python_skill = Skill(name="Python", category_id=cat_prog.id, description="Backend python")
    ui_skill = Skill(name="UI/UX Design", category_id=cat_design.id, description="Figma & wireframing")
    extra_skill = Skill(name="Public Speaking", category_id=cat_design.id, description="Oratory")
    db.session.add_all([python_skill, ui_skill, extra_skill])
    db.session.commit()

    # Student A: Teaches Python, Learns UI/UX Design
    SkillService.add_user_skill(student_user.id, python_skill.id, 'teach', 'advanced')
    SkillService.add_user_skill(student_user.id, ui_skill.id, 'learn', 'beginner')

    # Student B: Teaches UI/UX Design, Learns Python
    SkillService.add_user_skill(second_student_user.id, ui_skill.id, 'teach', 'advanced')
    SkillService.add_user_skill(second_student_user.id, python_skill.id, 'learn', 'intermediate')

    return {
        'student_a': student_user,
        'student_b': second_student_user,
        'python_skill': python_skill,
        'ui_skill': ui_skill,
        'extra_skill': extra_skill
    }


def test_create_exchange_request_success(app, setup_exchange_environment):
    """Verify student A can send a valid reciprocal exchange proposal to student B."""
    env = setup_exchange_environment
    req, error = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id,
        message="Hello Priya! I'd love to learn UI/UX design from you in exchange for Python tutoring."
    )

    assert error is None
    assert req is not None
    assert req.id is not None
    assert req.sender_id == env['student_a'].id
    assert req.receiver_id == env['student_b'].id
    assert req.offered_skill_id == env['python_skill'].id
    assert req.requested_skill_id == env['ui_skill'].id
    assert req.status == 'pending'
    assert req.is_pending is True


def test_reject_self_exchange_request(app, setup_exchange_environment):
    """Verify student cannot send an exchange request to themselves."""
    env = setup_exchange_environment
    req, error = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_a'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    assert req is None
    assert "cannot send an exchange request to yourself" in error.lower()


def test_reject_unrelated_offered_skill(app, setup_exchange_environment):
    """Verify student cannot offer a skill they do not have in their TEACH list."""
    env = setup_exchange_environment
    # Student A does NOT teach extra_skill
    req, error = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['extra_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    assert req is None
    assert "teach" in error.lower()


def test_reject_unrelated_requested_skill_not_in_receiver_teach(app, setup_exchange_environment):
    """Verify student cannot request a skill that the receiver does not teach."""
    env = setup_exchange_environment
    # Add extra_skill to Student A's LEARN list
    SkillService.add_user_skill(env['student_a'].id, env['extra_skill'].id, 'learn', 'beginner')

    # Student B does NOT teach extra_skill
    req, error = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['extra_skill'].id
    )

    assert req is None
    assert "does not offer to teach" in error


def test_reject_requested_skill_not_in_sender_learn(app, setup_exchange_environment):
    """Verify student cannot request a skill that is not in their own LEARN portfolio."""
    env = setup_exchange_environment
    # Make student B also teach extra_skill
    SkillService.add_user_skill(env['student_b'].id, env['extra_skill'].id, 'teach', 'advanced')

    # Student A does NOT have extra_skill in their LEARN list
    req, error = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['extra_skill'].id
    )

    assert req is None
    assert "learn" in error.lower()


def test_prevent_duplicate_active_pending_request(app, setup_exchange_environment):
    """Verify student cannot send duplicate pending requests for the same skills to the same peer."""
    env = setup_exchange_environment
    req1, error1 = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    assert error1 is None

    # Attempt second request with identical parameters
    req2, error2 = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    assert req2 is None
    assert "already have a pending exchange request" in error2.lower()


def test_incoming_and_outgoing_request_filtering(app, setup_exchange_environment):
    """Verify get_user_requests separates incoming and outgoing requests properly."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    # Student A's view
    a_reqs = ExchangeService.get_user_requests(env['student_a'].id)
    assert len(a_reqs['outgoing']) == 1
    assert len(a_reqs['incoming']) == 0
    assert a_reqs['outgoing'][0].id == req.id

    # Student B's view
    b_reqs = ExchangeService.get_user_requests(env['student_b'].id)
    assert len(b_reqs['incoming']) == 1
    assert len(b_reqs['outgoing']) == 0
    assert b_reqs['incoming'][0].id == req.id


def test_accept_exchange_request(app, setup_exchange_environment):
    """Verify receiver can accept an incoming pending request."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    success, error = ExchangeService.respond_to_request(
        request_id=req.id,
        user_id=env['student_b'].id,
        action='accept'
    )
    assert success is True
    assert error is None
    assert req.status == 'accepted'
    assert req.is_accepted is True


def test_reject_exchange_request(app, setup_exchange_environment):
    """Verify receiver can reject an incoming pending request."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    success, error = ExchangeService.respond_to_request(
        request_id=req.id,
        user_id=env['student_b'].id,
        action='reject'
    )
    assert success is True
    assert error is None
    assert req.status == 'rejected'
    assert req.is_rejected is True


def test_cancel_exchange_request_by_sender(app, setup_exchange_environment):
    """Verify sender can cancel their own outgoing pending request."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    success, error = ExchangeService.cancel_request(
        request_id=req.id,
        user_id=env['student_a'].id
    )
    assert success is True
    assert error is None
    assert req.status == 'cancelled'
    assert req.is_cancelled is True


def test_invalid_status_transitions_on_request(app, setup_exchange_environment):
    """Verify that once a request is accepted/rejected/cancelled, further status changes are rejected."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    # First accept
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')
    assert req.status == 'accepted'

    # Attempt to reject an already accepted request
    success, error = ExchangeService.respond_to_request(req.id, env['student_b'].id, 'reject')
    assert success is False
    assert "cannot change request with status 'accepted'" in error.lower()

    # Attempt to cancel an accepted request
    success2, error2 = ExchangeService.cancel_request(req.id, env['student_a'].id)
    assert success2 is False
    assert "cannot cancel request with status 'accepted'" in error2.lower()


def test_unauthorized_user_cannot_respond_or_cancel_request(app, setup_exchange_environment):
    """Verify authorization: sender cannot accept/reject; receiver cannot cancel; 3rd party cannot touch."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    # Sender cannot accept their own request
    s1, e1 = ExchangeService.respond_to_request(req.id, env['student_a'].id, 'accept')
    assert s1 is False
    assert "only the recipient can accept or reject" in e1.lower()

    # Receiver cannot cancel the request
    s2, e2 = ExchangeService.cancel_request(req.id, env['student_b'].id)
    assert s2 is False
    assert "only the sender can cancel" in e2.lower()

    # 3rd party cannot accept, reject, or cancel
    s3, e3 = ExchangeService.respond_to_request(req.id, 9999, 'accept')
    assert s3 is False
    assert "unauthorized" in e3.lower()


def test_unauthorized_access_to_request_details(client, second_student_user, setup_exchange_environment):
    """Verify third-party student cannot view an exchange request they are not part of."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )

    # Create a 3rd student
    from app.services.auth_service import AuthService
    third_user, _ = AuthService.register_user(
        name="Charlie Third",
        email="charlie@college.edu",
        password="password123",
        role="student"
    )

    # Login as third user
    client.post('/auth/login', data={'email': 'charlie@college.edu', 'password': 'password123'}, follow_redirects=True)
    res = client.get(f'/exchanges/{req.id}')
    assert res.status_code == 404


def test_schedule_session_success_after_acceptance(app, setup_exchange_environment):
    """Verify learning session can be scheduled after an exchange request is accepted."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')

    future_time = datetime.now() + timedelta(days=2, hours=10)
    sess, error = ExchangeService.schedule_session(
        request_id=req.id,
        user_id=env['student_a'].id,
        scheduled_at=future_time,
        duration_minutes=90,
        mode='online',
        meeting_details="https://meet.google.com/abc-def-ghi",
        notes="First session: Python variables and Figma components"
    )

    assert error is None
    assert sess is not None
    assert sess.id is not None
    assert sess.request_id == req.id
    assert sess.status == 'scheduled'
    assert sess.duration_minutes == 90
    assert sess.is_scheduled is True
    assert sess.is_participant(env['student_a'].id) is True
    assert sess.is_participant(env['student_b'].id) is True


def test_prevent_scheduling_for_pending_or_rejected_request(app, setup_exchange_environment):
    """Verify session scheduling fails if request is pending, rejected, or cancelled."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    # Request is still pending
    future_time = datetime.now() + timedelta(days=1)
    sess, err = ExchangeService.schedule_session(req.id, env['student_a'].id, future_time)
    assert sess is None
    assert "only be scheduled for an accepted exchange request" in err.lower()

    # Reject request and verify it still fails
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'reject')
    sess2, err2 = ExchangeService.schedule_session(req.id, env['student_a'].id, future_time)
    assert sess2 is None
    assert "only be scheduled for an accepted exchange request" in err2.lower()


def test_prevent_past_date_session_scheduling(app, setup_exchange_environment):
    """Verify session date and time cannot be in the past."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')

    past_time = datetime.now() - timedelta(days=2)
    sess, err = ExchangeService.schedule_session(req.id, env['student_a'].id, past_time)
    assert sess is None
    assert "cannot be in the past" in err.lower()


def test_authorized_participants_can_view_session(auth_client, client, setup_exchange_environment):
    """Verify authorized participants can view session details and third parties are blocked."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')
    sess, _ = ExchangeService.schedule_session(
        req.id,
        env['student_a'].id,
        datetime.now() + timedelta(days=2)
    )

    # Participant (Student A - auth_client) can view session
    res = auth_client.get(f'/exchanges/sessions/{sess.id}')
    assert res.status_code == 200
    assert b"Learning Session" in res.data
    assert b"Priya Patel" in res.data


def test_complete_scheduled_session(app, setup_exchange_environment):
    """Verify participant can mark a scheduled session as completed."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')
    sess, _ = ExchangeService.schedule_session(
        req.id,
        env['student_a'].id,
        datetime.now() + timedelta(days=2)
    )

    success, error = ExchangeService.complete_session(sess.id, env['student_b'].id)
    assert success is True
    assert error is None
    assert sess.status == 'completed'
    assert sess.is_completed is True


def test_cancel_scheduled_session(app, setup_exchange_environment):
    """Verify participant can cancel a scheduled session."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')
    sess, _ = ExchangeService.schedule_session(
        req.id,
        env['student_a'].id,
        datetime.now() + timedelta(days=2)
    )

    success, error = ExchangeService.cancel_session(sess.id, env['student_a'].id)
    assert success is True
    assert error is None
    assert sess.status == 'cancelled'
    assert sess.is_cancelled is True


def test_invalid_session_state_transitions(app, setup_exchange_environment):
    """Verify a completed session cannot be cancelled, and a cancelled session cannot be marked completed directly."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')
    sess, _ = ExchangeService.schedule_session(
        req.id,
        env['student_a'].id,
        datetime.now() + timedelta(days=2)
    )

    # Complete session
    ExchangeService.complete_session(sess.id, env['student_a'].id)
    assert sess.status == 'completed'

    # Cannot cancel a completed session
    s1, e1 = ExchangeService.cancel_session(sess.id, env['student_a'].id)
    assert s1 is False
    assert "cannot cancel a session that is 'completed'" in e1.lower()


def test_reschedule_cancelled_session_policy(app, setup_exchange_environment):
    """Verify documented rescheduling policy: a cancelled session can be rescheduled with a new date."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')
    sess, _ = ExchangeService.schedule_session(
        req.id,
        env['student_a'].id,
        datetime.now() + timedelta(days=2)
    )

    # Cancel session
    ExchangeService.cancel_session(sess.id, env['student_a'].id)
    assert sess.status == 'cancelled'

    # Reschedule with new date
    new_time = datetime.now() + timedelta(days=5, hours=2)
    rescheduled_sess, error = ExchangeService.schedule_session(
        request_id=req.id,
        user_id=env['student_b'].id,
        scheduled_at=new_time,
        duration_minutes=75,
        mode='in_person',
        meeting_details="Campus Library Room 402"
    )

    assert error is None
    assert rescheduled_sess.status == 'scheduled'
    assert rescheduled_sess.duration_minutes == 75
    assert rescheduled_sess.mode == 'in_person'


def test_session_history_separation(app, setup_exchange_environment):
    """Verify get_user_sessions cleanly categorizes into upcoming and past sessions."""
    env = setup_exchange_environment
    req, _ = ExchangeService.create_request(
        sender_id=env['student_a'].id,
        receiver_id=env['student_b'].id,
        offered_skill_id=env['python_skill'].id,
        requested_skill_id=env['ui_skill'].id
    )
    ExchangeService.respond_to_request(req.id, env['student_b'].id, 'accept')
    sess, _ = ExchangeService.schedule_session(
        req.id,
        env['student_a'].id,
        datetime.now() + timedelta(days=2)
    )

    # Currently scheduled: in upcoming
    history = ExchangeService.get_user_sessions(env['student_a'].id)
    assert len(history['upcoming']) == 1
    assert len(history['past']) == 0

    # Mark completed: transitions to past
    ExchangeService.complete_session(sess.id, env['student_a'].id)
    history2 = ExchangeService.get_user_sessions(env['student_a'].id)
    assert len(history2['upcoming']) == 0
    assert len(history2['past']) == 1


def test_unauthenticated_redirected_from_exchange_and_session_routes(client):
    """Verify guest cannot access exchange or session endpoints."""
    assert client.get('/exchanges/').status_code == 302
    assert client.get('/exchanges/new').status_code == 302
    assert client.get('/exchanges/1').status_code == 302
    assert client.get('/exchanges/sessions').status_code == 302
    assert client.get('/exchanges/sessions/1').status_code == 302
