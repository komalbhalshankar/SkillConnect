"""
Unit and integration tests for Skill Discovery and Rule-Based Matching (Phase 3 Module 3).
Tests deterministic matching formula, reciprocal and one-way compatibility,
score explanations, ranking, tie-breaking, and database-backed student discovery.
"""
import pytest
from app.extensions import db
from app.models.user import User
from app.models.skill import SkillCategory, Skill, UserSkill
from app.services.skill_service import SkillService
from app.services.matching_service import MatchingService

@pytest.fixture
def matched_peer_setup(app, student_user, second_student_user, sample_category):
    """
    Setup two students with a full reciprocal match:
    Student A (Aarav): TEACH Python (Advanced), LEARN Java (Beginner)
    Student B (Priya): TEACH Java (Advanced), LEARN Python (Intermediate)
    """
    python_skill = Skill.query.filter_by(name="Python").first()
    if not python_skill:
        python_skill = Skill(category_id=sample_category.id, name="Python", description="Python dev")
        db.session.add(python_skill)

    java_skill = Skill.query.filter_by(name="Java").first()
    if not java_skill:
        java_skill = Skill(category_id=sample_category.id, name="Java", description="Java dev")
        db.session.add(java_skill)
    db.session.commit()

    # Student A (Aarav): TEACH Python (Adv), LEARN Java (Beg)
    SkillService.add_user_skill(user_id=student_user.id, skill_id=python_skill.id, skill_type='teach', proficiency='advanced')
    SkillService.add_user_skill(user_id=student_user.id, skill_id=java_skill.id, skill_type='learn', proficiency='beginner')

    # Student B (Priya): TEACH Java (Adv), LEARN Python (Inter)
    SkillService.add_user_skill(user_id=second_student_user.id, skill_id=java_skill.id, skill_type='teach', proficiency='advanced')
    SkillService.add_user_skill(user_id=second_student_user.id, skill_id=python_skill.id, skill_type='learn', proficiency='intermediate')

    return student_user, second_student_user, python_skill, java_skill

def test_full_reciprocal_matching_score(app, matched_peer_setup):
    """Full reciprocal match earns 40 (fwd) + 40 (rev) + 10 (cat) + 10 (prof) = 100 points."""
    student_a, student_b, python_skill, java_skill = matched_peer_setup

    match_data = MatchingService.calculate_compatibility(student_a, student_b)
    assert match_data is not None
    assert match_data['is_reciprocal'] is True
    assert match_data['match_type'] == 'Reciprocal'
    assert match_data['score'] == 100

    # Verify matched skill details
    assert len(match_data['fwd_skills']) == 1
    assert match_data['fwd_skills'][0]['skill_name'] == "Java"
    assert len(match_data['rev_skills']) == 1
    assert match_data['rev_skills'][0]['skill_name'] == "Python"

    # Verify score explanation
    assert any("+40 pts" in item for item in match_data['score_breakdown'])
    assert any("+10 pts: Skill category alignment" in item for item in match_data['score_breakdown'])
    assert any("+10 pts: Proficiency level compatibility" in item for item in match_data['score_breakdown'])

def test_one_way_matching_score(app, student_user, second_student_user, sample_category):
    """One-way match awards 40 points base plus category/proficiency bonuses where applicable."""
    python_skill = Skill(category_id=sample_category.id, name="Python")
    db.session.add(python_skill)
    db.session.commit()

    # Student A wants to LEARN Python
    SkillService.add_user_skill(user_id=student_user.id, skill_id=python_skill.id, skill_type='learn', proficiency='beginner')

    # Student B TEACHES Python (Advanced), but wants to learn nothing that Student A offers
    SkillService.add_user_skill(user_id=second_student_user.id, skill_id=python_skill.id, skill_type='teach', proficiency='advanced')

    match_data = MatchingService.calculate_compatibility(student_user, second_student_user)
    assert match_data is not None
    assert match_data['is_reciprocal'] is False
    assert match_data['match_type'] == 'One-Way'
    # 40 (fwd) + 10 (cat) + 10 (prof: teacher adv >= learner beg) = 60
    assert match_data['score'] == 60
    assert len(match_data['fwd_skills']) == 1
    assert len(match_data['rev_skills']) == 0

def test_disjoint_skills_return_no_match(student_user, second_student_user, sample_category):
    """Students with zero complementary skill overlap produce None."""
    skill_a = Skill(category_id=sample_category.id, name="Go Programming")
    skill_b = Skill(category_id=sample_category.id, name="Ruby on Rails")
    db.session.add_all([skill_a, skill_b])
    db.session.commit()

    SkillService.add_user_skill(user_id=student_user.id, skill_id=skill_a.id, skill_type='teach')
    SkillService.add_user_skill(user_id=second_student_user.id, skill_id=skill_b.id, skill_type='learn')

    match_data = MatchingService.calculate_compatibility(student_user, second_student_user)
    assert match_data is None

def test_self_matching_prevented(student_user, sample_skill):
    """Evaluating compatibility with oneself strictly returns None."""
    SkillService.add_user_skill(user_id=student_user.id, skill_id=sample_skill.id, skill_type='teach')
    match_data = MatchingService.calculate_compatibility(student_user, student_user)
    assert match_data is None

def test_score_bounds_between_0_and_100(student_user, second_student_user, sample_category):
    """Extreme combinations never produce scores below 0 or above 100."""
    skills = [Skill(category_id=sample_category.id, name=f"Skill_{i}") for i in range(5)]
    db.session.add_all(skills)
    db.session.commit()

    # Link multiple skills to both
    for s in skills:
        SkillService.add_user_skill(student_user.id, s.id, 'teach', 'advanced')
        SkillService.add_user_skill(student_user.id, s.id, 'learn', 'beginner')
        SkillService.add_user_skill(second_student_user.id, s.id, 'teach', 'advanced')
        SkillService.add_user_skill(second_student_user.id, s.id, 'learn', 'beginner')

    match_data = MatchingService.calculate_compatibility(student_user, second_student_user)
    assert match_data is not None
    assert 0 <= match_data['score'] <= 100

def test_deterministic_ranking(app, student_user, second_student_user, sample_category):
    """Reciprocal matches are ranked before one-way matches."""
    # Create third student
    from app.services.auth_service import AuthService
    third_student, _ = AuthService.register_user(name="Dev Singh", email="dev@college.edu", password="passWord123")

    s1 = Skill(category_id=sample_category.id, name="React")
    s2 = Skill(category_id=sample_category.id, name="Django")
    db.session.add_all([s1, s2])
    db.session.commit()

    # student_user: TEACH React, LEARN Django
    SkillService.add_user_skill(student_user.id, s1.id, 'teach')
    SkillService.add_user_skill(student_user.id, s2.id, 'learn')

    # second_student (Priya): One-way only (TEACH Django)
    SkillService.add_user_skill(second_student_user.id, s2.id, 'teach')

    # third_student (Dev): Full Reciprocal (TEACH Django, LEARN React)
    SkillService.add_user_skill(third_student.id, s2.id, 'teach')
    SkillService.add_user_skill(third_student.id, s1.id, 'learn')

    matches = MatchingService.get_matches_for_user(student_user)
    assert len(matches) == 2
    # Reciprocal match (Dev) must be ranked first
    assert matches[0]['candidate'].id == third_student.id
    assert matches[0]['is_reciprocal'] is True
    # One-way match (Priya) must be ranked second
    assert matches[1]['candidate'].id == second_student_user.id
    assert matches[1]['is_reciprocal'] is False

def test_discovery_search_by_skill_name(auth_client, matched_peer_setup):
    """Student can search for peers by skill name; current user is excluded."""
    student_a, student_b, _, _ = matched_peer_setup
    response = auth_client.get('/matching/discover?q=Java')
    assert response.status_code == 200
    html = response.get_data(as_text=True)

    # Priya teaches Java -> Priya must appear as a candidate card
    assert f"/matching/student/{student_b.id}" in html
    assert "Priya Patel" in html

    # Current user (Aarav) must be strictly excluded from discovery results cards
    assert f"/matching/student/{student_a.id}" not in html

def test_discovery_filter_by_category_and_proficiency(auth_client, matched_peer_setup, sample_category):
    """Student can filter discovery results by category and proficiency level."""
    response = auth_client.get(f'/matching/discover?category_id={sample_category.id}&proficiency=advanced')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Priya Patel" in html

def test_discovery_empty_search_results(auth_client):
    """Searching for a nonexistent skill displays clear empty state message."""
    response = auth_client.get('/matching/discover?q=NonExistentSkillXYZ123')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "No Students Match Your Filters" in html

def test_matching_recommendations_page(auth_client, matched_peer_setup):
    """Authenticated student can view their matching recommendations."""
    response = auth_client.get('/matching/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Matching Recommendations" in html
    assert "Priya Patel" in html
    assert "100% Match" in html or "% Match" in html
    assert "Two-Way Reciprocal" in html

def test_student_detail_profile_inspection(auth_client, second_student_user, matched_peer_setup):
    """Viewing candidate student details shows academic profile and compatibility breakdown."""
    response = auth_client.get(f'/matching/student/{second_student_user.id}')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Priya Patel" in html
    assert "Exchange Compatibility with You" in html
    assert "Java" in html
    assert "Python" in html
    assert "Coming in Phase 4" in html

def test_unauthenticated_cannot_access_matching_or_discovery(client):
    """Unauthenticated users attempting to access discovery or matching are redirected to login."""
    res1 = client.get('/matching/')
    assert res1.status_code == 302
    assert '/auth/login' in res1.headers['Location']

    res2 = client.get('/matching/discover')
    assert res2.status_code == 302
    assert '/auth/login' in res2.headers['Location']
