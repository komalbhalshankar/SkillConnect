"""
End-to-End (E2E) Integration Tests for SkillConnect.
Executes the complete student exchange lifecycle and administrative governance flows.
"""
from datetime import datetime, timezone, timedelta, date, time
import pytest
from app.extensions import db
from app.models.user import User
from app.models.skill import SkillCategory, Skill, UserSkill
from app.models.exchange import ExchangeRequest, ExchangeSession
from app.models.rating import Rating
from app.services.skill_service import SkillService

def test_student_complete_e2e_workflow(client, app):
    """
    Complete End-to-End Workflow:
    Register Student A
    -> Log in as Student A & Complete Profile
    -> Register Student B
    -> Add Teach/Learn Skills for both
    -> Discover Student B
    -> Verify Matching (Reciprocal 100%)
    -> Send Exchange Request
    -> Log in as Student B
    -> Accept Request
    -> Schedule Session
    -> Complete Session
    -> Submit Rating and Feedback (Bilateral)
    -> View Updated Dashboard and Reviews
    """
    # 0. Base setup: Category & Skills
    with app.app_context():
        cat = SkillCategory(name="Programming", icon="bi-code", description="Code skills")
        db.session.add(cat)
        db.session.commit()
        sk_py = Skill(category_id=cat.id, name="Python", description="Backend Python")
        sk_ui = Skill(category_id=cat.id, name="UI/UX Design", description="Figma wireframing")
        db.session.add_all([sk_py, sk_ui])
        db.session.commit()
        py_id = sk_py.id
        ui_id = sk_ui.id

    # 1. Register Student A (Aarav)
    res_reg_a = client.post('/auth/register', data={
        'name': 'Aarav Sharma',
        'email': 'aarav@college.edu',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'college': 'Dept of CS, National Institute',
        'bio': 'Passionate Python developer.',
        'availability': 'Weekday evenings'
    }, follow_redirects=True)
    assert res_reg_a.status_code == 200
    assert b"created successfully" in res_reg_a.data

    # Log in Student A
    res_login_a = client.post('/auth/login', data={
        'email': 'aarav@college.edu',
        'password': 'Password@123'
    }, follow_redirects=True)
    assert res_login_a.status_code == 200
    assert b"Welcome back, Aarav Sharma!" in res_login_a.data

    # 2. Complete/Update Profile
    res_prof_a = client.post('/profile', data={
        'name': 'Aarav Sharma',
        'college': 'National Institute of Technology',
        'bio': 'Passionate Python and systems programmer.',
        'availability': 'Mon to Thu 6 PM - 9 PM'
    }, follow_redirects=True)
    assert res_prof_a.status_code == 200
    assert b"profile has been updated successfully" in res_prof_a.data

    # Log out Student A
    client.get('/auth/logout', follow_redirects=True)

    # 3. Register Student B (Priya)
    res_reg_b = client.post('/auth/register', data={
        'name': 'Priya Patel',
        'email': 'priya@college.edu',
        'password': 'Password@123',
        'confirm_password': 'Password@123',
        'college': 'School of Design, Tech University',
        'bio': 'Figma UI/UX enthusiast.',
        'availability': 'Weekends'
    }, follow_redirects=True)
    assert res_reg_b.status_code == 200
    assert b"created successfully" in res_reg_b.data

    # 4. Add Skills:
    # Aarav: Teaches Python (Adv), Learns UI/UX Design (Beg)
    # Priya: Teaches UI/UX Design (Adv), Learns Python (Int)
    with app.app_context():
        u_aarav = User.query.filter_by(email='aarav@college.edu').first()
        u_priya = User.query.filter_by(email='priya@college.edu').first()
        SkillService.add_user_skill(u_aarav.id, py_id, 'teach', 'advanced')
        SkillService.add_user_skill(u_aarav.id, ui_id, 'learn', 'beginner')
        SkillService.add_user_skill(u_priya.id, ui_id, 'teach', 'advanced')
        SkillService.add_user_skill(u_priya.id, py_id, 'learn', 'intermediate')

    # 5. Log in as Student A & Discover Student B
    client.post('/auth/login', data={
        'email': 'aarav@college.edu',
        'password': 'Password@123'
    }, follow_redirects=True)

    res_disc = client.get('/matching/discover?q=Design')
    assert res_disc.status_code == 200
    assert b"Priya Patel" in res_disc.data

    # Check Matching recommendations (Reciprocal 100%)
    res_match = client.get('/matching/')
    assert res_match.status_code == 200
    assert b"Priya Patel" in res_match.data
    assert b"100%" in res_match.data
    assert b"Reciprocal" in res_match.data

    # 6. Student A sends exchange request to Student B
    with app.app_context():
        u_priya = User.query.filter_by(email='priya@college.edu').first()
        priya_id = u_priya.id

    res_new_req = client.post(f'/exchanges/new?receiver_id={priya_id}', data={
        'receiver_id': priya_id,
        'offered_skill_id': py_id,
        'requested_skill_id': ui_id,
        'message': "Hello Priya! Let's do a peer exchange on Python and Figma."
    }, follow_redirects=True)
    assert res_new_req.status_code == 200
    assert b"Exchange request successfully sent" in res_new_req.data

    # Log out Student A
    client.get('/auth/logout', follow_redirects=True)

    # 7. Log in as Student B (Priya) and Accept Request
    client.post('/auth/login', data={
        'email': 'priya@college.edu',
        'password': 'Password@123'
    }, follow_redirects=True)

    with app.app_context():
        req = ExchangeRequest.query.filter_by(receiver_id=priya_id, status='pending').first()
        assert req is not None
        req_id = req.id

    # View incoming requests
    res_inbox = client.get('/exchanges/?tab=incoming')
    assert res_inbox.status_code == 200
    assert b"Aarav Sharma" in res_inbox.data

    # Priya accepts request
    res_accept = client.post(f'/exchanges/respond/{req_id}/accept', follow_redirects=True)
    assert res_accept.status_code == 200
    assert b"accepted" in res_accept.data

    # 8. Schedule Session for accepted request
    future_date = date.today() + timedelta(days=2)
    res_sched = client.post(f'/exchanges/schedule/{req_id}', data={
        'scheduled_date': future_date.strftime('%Y-%m-%d'),
        'scheduled_time': '16:00',
        'duration_minutes': 60,
        'mode': 'online',
        'meeting_details': 'https://meet.google.com/skillconnect-e2e',
        'notes': 'Discussion on Figma prototyping and Python fundamentals.'
    }, follow_redirects=True)
    assert res_sched.status_code == 200
    assert b"session successfully scheduled" in res_sched.data

    with app.app_context():
        sess = ExchangeSession.query.filter_by(request_id=req_id).first()
        assert sess is not None
        assert sess.status == 'scheduled'
        sess_id = sess.id

    # 9. Complete the Session
    res_comp = client.post(f'/exchanges/sessions/{sess_id}/complete', follow_redirects=True)
    assert res_comp.status_code == 200
    assert b"Session marked as completed" in res_comp.data

    # 10. Priya submits rating and feedback for Aarav
    res_rate_priya = client.post(f'/exchanges/sessions/{sess_id}/rate', data={
        'score': 5,
        'feedback': "Aarav explained Python concepts thoroughly and with great examples!"
    }, follow_redirects=True)
    assert res_rate_priya.status_code == 200
    assert b"Thank you! Your rating and feedback" in res_rate_priya.data

    # Log out Student B
    client.get('/auth/logout', follow_redirects=True)

    # Log in as Student A (Aarav) and submit rating for Priya
    client.post('/auth/login', data={
        'email': 'aarav@college.edu',
        'password': 'Password@123'
    }, follow_redirects=True)

    res_rate_aarav = client.post(f'/exchanges/sessions/{sess_id}/rate', data={
        'score': 5,
        'feedback': "Priya wireframing guidance was incredible and super hands-on."
    }, follow_redirects=True)
    assert res_rate_aarav.status_code == 200
    assert b"Thank you! Your rating and feedback" in res_rate_aarav.data

    # 11. View Updated Student A Dashboard and Profile
    res_dash_a = client.get('/dashboard')
    assert res_dash_a.status_code == 200
    assert b"Student Dashboard" in res_dash_a.data
    assert b"Aarav Sharma" in res_dash_a.data
    assert b"Peer Review Star Breakdown" in res_dash_a.data

    res_prof_view_a = client.get('/profile')
    assert res_prof_view_a.status_code == 200
    assert b"Peer Ratings &amp; Reviews Received" in res_prof_view_a.data
    assert b"Aarav explained Python concepts" in res_prof_view_a.data
    assert b"5.0" in res_prof_view_a.data

def test_admin_complete_e2e_workflow(client, app, admin_user, student_user):
    """
    Complete Administrator Workflow:
    - Log in as admin
    - Access /admin portal
    - Add skill category
    - Add standardized skill under category
    - Verify regular student access forbidden (HTTP 403)
    """
    # 1. Admin login
    res_login = client.post('/auth/login', data={
        'email': 'admin@college.edu',
        'password': 'adminSecretPassword789'
    }, follow_redirects=True)
    assert res_login.status_code == 200

    # 2. Access Admin Portal
    res_admin = client.get('/admin')
    assert res_admin.status_code == 200
    assert b"Admin Portal" in res_admin.data

    # 3. Add skill category
    res_add_cat = client.post('/admin/categories/add', data={
        'name': 'Cloud Computing',
        'icon': 'bi-cloud',
        'description': 'AWS, GCP, and cloud DevOps'
    }, follow_redirects=True)
    assert res_add_cat.status_code == 200
    assert b"created successfully" in res_add_cat.data

    with app.app_context():
        new_cat = SkillCategory.query.filter_by(name='Cloud Computing').first()
        assert new_cat is not None
        cat_id = new_cat.id

    # 4. Add standardized skill under category
    res_add_skill = client.post('/admin/skills/add', data={
        'category_id': cat_id,
        'name': 'Docker Containerization',
        'description': 'Dockerfiles, container orchestration, and images.'
    }, follow_redirects=True)
    assert res_add_skill.status_code == 200
    assert b"added to category" in res_add_skill.data

    # 5. Log out Admin
    client.get('/auth/logout', follow_redirects=True)

    # 6. Log in as Student and verify /admin returns 403 Forbidden
    client.post('/auth/login', data={
        'email': 'aarav@college.edu',
        'password': 'securePassword123'
    }, follow_redirects=True)

    res_forbidden = client.get('/admin')
    assert res_forbidden.status_code == 403
