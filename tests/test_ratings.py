"""
Automated pytest suite for Phase 5: Rating, Feedback and Dashboard.
Verifies business rules, edge cases, data isolation, and UI routes.
"""
from datetime import datetime, timezone, timedelta
import pytest
from app.extensions import db
from app.models.user import User
from app.models.skill import SkillCategory, Skill, UserSkill
from app.models.exchange import ExchangeRequest, ExchangeSession
from app.models.rating import Rating
from app.services.auth_service import AuthService
from app.services.skill_service import SkillService
from app.services.exchange_service import ExchangeService
from app.services.rating_service import RatingService
from app.services.stats_service import StatsService

@pytest.fixture
def third_student_user(app):
    """Create and return a third registered student (unrelated to exchange)."""
    user, _ = AuthService.register_user(
        name="Rohan Gupta",
        email="rohan@college.edu",
        password="rohanPassword999",
        college="School of Information Technology",
        bio="Full stack and mobile enthusiast.",
        availability="Flexible",
        role="student"
    )
    return user

@pytest.fixture
def scheduled_session(app, student_user, second_student_user, sample_skill, second_skill):
    """
    Set up a scheduled learning exchange session between student_user and second_student_user.
    """
    SkillService.add_user_skill(student_user.id, sample_skill.id, 'teach', 'advanced')
    SkillService.add_user_skill(student_user.id, second_skill.id, 'learn', 'beginner')
    SkillService.add_user_skill(second_student_user.id, second_skill.id, 'teach', 'intermediate')
    SkillService.add_user_skill(second_student_user.id, sample_skill.id, 'learn', 'beginner')

    # Aarav proposes exchange to Priya
    req, err = ExchangeService.create_request(
        sender_id=student_user.id,
        receiver_id=second_student_user.id,
        offered_skill_id=sample_skill.id,
        requested_skill_id=second_skill.id,
        message="Let's exchange Python and Java knowledge."
    )
    assert err is None

    # Priya accepts
    ExchangeService.respond_to_request(req.id, second_student_user.id, 'accept')

    # Schedule session in the future
    sess_time = datetime.now(timezone.utc) + timedelta(days=1)
    session, serr = ExchangeService.schedule_session(
        request_id=req.id,
        user_id=student_user.id,
        scheduled_at=sess_time,
        duration_minutes=60,
        mode="online",
        meeting_details="https://meet.jit.si/skillconnect-test"
    )
    assert serr is None
    return session

@pytest.fixture
def completed_exchange_session(scheduled_session, student_user):
    """Set up a completed learning exchange session."""
    ExchangeService.complete_session(scheduled_session.id, student_user.id)
    return scheduled_session

def test_valid_rating_submission_after_completion(app, completed_exchange_session, student_user, second_student_user):
    """Test valid rating submission by an exchange participant after session completion."""
    session = completed_exchange_session
    assert session.status == 'completed'

    rating, err = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=student_user.id,
        score=5,
        feedback="Priya explained Java OOP concepts exceptionally well!"
    )

    assert err is None
    assert rating is not None
    assert rating.score == 5
    assert rating.feedback == "Priya explained Java OOP concepts exceptionally well!"
    assert rating.reviewer_id == student_user.id
    assert rating.reviewee_id == second_student_user.id

    # Verify reviewee's stats
    summary = RatingService.get_user_ratings_summary(second_student_user.id)
    assert summary['review_count'] == 1
    assert summary['average_rating'] == 5.0
    assert summary['distribution'][5] == 1

def test_rejection_of_ratings_before_completion(app, scheduled_session, student_user):
    """Test that ratings cannot be submitted for a scheduled session that is not completed."""
    session = scheduled_session
    assert session.status == 'scheduled'

    rating, err = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=student_user.id,
        score=4,
        feedback="Pre-mature review attempt"
    )
    assert rating is None
    assert "Completed" in err

def test_rejection_of_ratings_for_cancelled_sessions(app, completed_exchange_session, student_user):
    """Test that ratings cannot be submitted for a cancelled session."""
    session = completed_exchange_session
    # Force session status to cancelled
    session.status = 'cancelled'
    db.session.commit()

    rating, err = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=student_user.id,
        score=3
    )
    assert rating is None
    assert "Completed" in err

def test_rejection_of_invalid_rating_values(app, completed_exchange_session, student_user):
    """Test rejection of scores outside the allowable integer range 1-5."""
    session = completed_exchange_session

    for invalid_score in [0, 6, -1, 10, "5"]:
        rating, err = RatingService.submit_rating(
            session_id=session.id,
            reviewer_id=student_user.id,
            score=invalid_score
        )
        assert rating is None
        assert "integer between 1 and 5" in err

def test_prevention_of_ratings_by_unrelated_users(app, completed_exchange_session, third_student_user):
    """Test that a third student not participating in the session cannot submit a rating."""
    session = completed_exchange_session
    rating, err = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=third_student_user.id,
        score=5,
        feedback="Unauthorized attempt"
    )
    assert rating is None
    assert "not a participant" in err

def test_prevention_of_duplicate_ratings(app, completed_exchange_session, student_user):
    """Test that a reviewer cannot submit more than one rating for the same session."""
    session = completed_exchange_session

    rating1, err1 = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=student_user.id,
        score=5,
        feedback="First review"
    )
    assert err1 is None
    assert rating1 is not None

    # Duplicate attempt
    rating2, err2 = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=student_user.id,
        score=4,
        feedback="Duplicate review attempt"
    )
    assert rating2 is None
    assert "already submitted" in err2

def test_independent_bilateral_ratings(app, completed_exchange_session, student_user, second_student_user):
    """
    Test that both participants can independently submit ratings for the same completed session.
    Aarav rates Priya (4 stars), Priya rates Aarav (5 stars).
    """
    session = completed_exchange_session

    # Aarav rates Priya
    r1, err1 = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=student_user.id,
        score=4,
        feedback="Great collaborative session."
    )
    assert err1 is None

    # Priya rates Aarav
    r2, err2 = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=second_student_user.id,
        score=5,
        feedback="Aarav was super helpful with Python algorithms!"
    )
    assert err2 is None

    assert session.has_user_rated(student_user.id) is True
    assert session.has_user_rated(second_student_user.id) is True

    # Check received averages
    assert student_user.average_rating == 5.0
    assert student_user.review_count == 1
    assert second_student_user.average_rating == 4.0
    assert second_student_user.review_count == 1

def test_average_rating_and_rounding(app, student_user, second_student_user, third_student_user):
    """Test accurate arithmetic average calculation with multiple reviews."""
    # Fake session dummy records for multi-review math verification
    cat = SkillCategory(name="Tech", icon="bi-laptop")
    db.session.add(cat)
    db.session.flush()
    sk = Skill(category_id=cat.id, name="Go")
    db.session.add(sk)
    db.session.flush()

    req1 = ExchangeRequest(sender_id=second_student_user.id, receiver_id=student_user.id, offered_skill_id=sk.id, requested_skill_id=sk.id, status='accepted')
    req2 = ExchangeRequest(sender_id=third_student_user.id, receiver_id=student_user.id, offered_skill_id=sk.id, requested_skill_id=sk.id, status='accepted')
    db.session.add_all([req1, req2])
    db.session.flush()

    s1 = ExchangeSession(request_id=req1.id, scheduled_at=datetime.now(timezone.utc), status='completed')
    s2 = ExchangeSession(request_id=req2.id, scheduled_at=datetime.now(timezone.utc), status='completed')
    db.session.add_all([s1, s2])
    db.session.flush()

    # Second student gives 4 stars, third gives 5 stars
    RatingService.submit_rating(s1.id, second_student_user.id, score=4)
    RatingService.submit_rating(s2.id, third_student_user.id, score=5)

    summary = RatingService.get_user_ratings_summary(student_user.id)
    assert summary['review_count'] == 2
    assert summary['average_rating'] == 4.5
    assert summary['distribution'][4] == 1
    assert summary['distribution'][5] == 1

def test_feedback_length_validation(app, completed_exchange_session, student_user):
    """Test that feedback comments exceeding 500 characters are rejected."""
    session = completed_exchange_session
    long_comment = "x" * 501

    rating, err = RatingService.submit_rating(
        session_id=session.id,
        reviewer_id=student_user.id,
        score=5,
        feedback=long_comment
    )
    assert rating is None
    assert "500 characters or fewer" in err

def test_nonexistent_session_rating(app, student_user):
    """Test safe handling when rating a non-existent session."""
    rating, err = RatingService.submit_rating(
        session_id=999999,
        reviewer_id=student_user.id,
        score=5
    )
    assert rating is None
    assert "Session not found" in err

def test_dashboard_stats_for_active_student(app, completed_exchange_session, student_user, second_student_user):
    """Verify that student dashboard metrics accurately reflect real database records."""
    session = completed_exchange_session
    RatingService.submit_rating(session.id, second_student_user.id, score=5, feedback="Excellent tutor")

    stats = StatsService.get_student_dashboard_stats(student_user)

    assert stats['teach_count'] == 1
    assert stats['learn_count'] == 1
    assert stats['total_skills'] == 2
    assert stats['completed_sessions_count'] == 1
    assert stats['review_count'] == 1
    assert stats['average_rating'] == 5.0
    assert len(stats['unrated_completed_sessions']) == 1  # Aarav hasn't rated Priya yet

    # Now Aarav rates Priya
    RatingService.submit_rating(session.id, student_user.id, score=4)
    stats_after = StatsService.get_student_dashboard_stats(student_user)
    assert len(stats_after['unrated_completed_sessions']) == 0

def test_dashboard_empty_state_for_new_user(app):
    """Verify that a brand new student with zero activity receives safe 0s and empty lists."""
    new_user, _ = AuthService.register_user(
        name="New Student",
        email="newstudent@college.edu",
        password="password123"
    )

    stats = StatsService.get_student_dashboard_stats(new_user)
    assert stats['total_skills'] == 0
    assert stats['compatible_matches_count'] == 0
    assert stats['total_requests'] == 0
    assert stats['total_sessions'] == 0
    assert stats['average_rating'] == 0.0
    assert stats['review_count'] == 0
    assert len(stats['upcoming_sessions']) == 0
    assert len(stats['recent_requests']) == 0
    assert len(stats['recent_ratings']) == 0

    # Verify chart totals are all 0
    assert stats['chart_data']['sessions']['total'] == 0
    assert stats['chart_data']['requests']['total'] == 0
    assert stats['chart_data']['ratings']['total'] == 0

def test_dashboard_cross_user_isolation(app, completed_exchange_session, student_user, third_student_user):
    """Verify that user A's private activity is not visible in user C's dashboard."""
    stats_c = StatsService.get_student_dashboard_stats(third_student_user)
    assert stats_c['total_sessions'] == 0
    assert stats_c['total_requests'] == 0
    assert stats_c['review_count'] == 0

def test_rating_route_workflow(app, client, completed_exchange_session, student_user, second_student_user):
    """Test full HTTP GET and POST flow for submitting a rating."""
    session = completed_exchange_session

    # Login as Aarav
    client.post('/auth/login', data={
        'email': 'aarav@college.edu',
        'password': 'securePassword123'
    }, follow_redirects=True)

    # GET rate page
    res_get = client.get(f'/exchanges/sessions/{session.id}/rate')
    assert res_get.status_code == 200
    assert b"Rate &amp; Review" in res_get.data
    assert b"Priya Patel" in res_get.data

    # POST valid rating
    res_post = client.post(f'/exchanges/sessions/{session.id}/rate', data={
        'score': 5,
        'feedback': "Learned a lot about design principles!"
    }, follow_redirects=True)

    assert res_post.status_code == 200
    assert b"Thank you! Your rating and feedback" in res_post.data

    # Attempting to access rate page again should redirect with info flash
    res_repeat = client.get(f'/exchanges/sessions/{session.id}/rate', follow_redirects=True)
    assert b"already submitted" in res_repeat.data

def test_dashboard_route_view(app, auth_client):
    """Test that /dashboard renders successfully with Chart.js and dynamic cards."""
    res = auth_client.get('/dashboard')
    assert res.status_code == 200
    assert b"Student Dashboard" in res.data
    assert b"Session Status Distribution" in res.data
    assert b"Peer Review Star Breakdown" in res.data

def test_profile_reviews_section_view(app, auth_client):
    """Test that /profile displays the Peer Ratings & Reviews Received section."""
    res = auth_client.get('/profile')
    assert res.status_code == 200
    assert b"Peer Ratings &amp; Reviews Received" in res.data
    assert b"No ratings yet." in res.data

def test_student_detail_reviews_view(app, auth_client, second_student_user):
    """Test that public student profile renders peer ratings and reviews."""
    res = auth_client.get(f'/matching/student/{second_student_user.id}')
    assert res.status_code == 200
    assert b"Peer Reviews &amp; Evaluations" in res.data
    assert b"No ratings yet." in res.data
