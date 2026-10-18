"""
Unit and integration tests for Skill Management (Phase 3).
Tests skill catalog taxonomy, student skill portfolio (Teach & Learn),
ownership enforcement, and administrator category/skill curation.
"""
import pytest
from app.extensions import db
from app.models.skill import SkillCategory, Skill, UserSkill
from app.services.skill_service import SkillService

def test_unauthenticated_redirected_from_skills(client):
    """Unauthenticated users must be redirected to the login page."""
    response = client.get('/skills/')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']

def test_student_can_view_skills_portfolio(auth_client, sample_category, sample_skill):
    """Authenticated student can view their skill portfolio page."""
    response = auth_client.get('/skills/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "My Skill Portfolio" in html
    assert "Skills I Can Teach" in html
    assert "Skills I Want to Learn" in html
    assert "Python" in html

def test_add_teach_skill_success(auth_client, student_user, sample_skill):
    """Student can add a skill to their Teach portfolio."""
    response = auth_client.post('/skills/add', data={
        'skill_id': sample_skill.id,
        'skill_type': 'teach',
        'proficiency': 'advanced',
        'notes': 'Experienced with OOP and Flask backend architecture'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Successfully added &#39;Python&#39; to your TEACH list!" in html or "Successfully added 'Python' to your TEACH list!" in html

    user_skill = UserSkill.query.filter_by(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach'
    ).first()
    assert user_skill is not None
    assert user_skill.proficiency == 'advanced'
    assert user_skill.notes == 'Experienced with OOP and Flask backend architecture'

def test_add_learn_skill_success(auth_client, student_user, second_skill):
    """Student can add a skill to their Learn wishlist."""
    response = auth_client.post('/skills/add', data={
        'skill_id': second_skill.id,
        'skill_type': 'learn',
        'proficiency': 'beginner',
        'notes': 'Preparing for campus interviews'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Successfully added &#39;Java&#39; to your LEARN list!" in html or "Successfully added 'Java' to your LEARN list!" in html

    user_skill = UserSkill.query.filter_by(
        user_id=student_user.id,
        skill_id=second_skill.id,
        skill_type='learn'
    ).first()
    assert user_skill is not None
    assert user_skill.proficiency == 'beginner'

def test_prevent_duplicate_skill_in_same_list(auth_client, student_user, sample_skill):
    """A student cannot add the exact same skill twice in their Teach list."""
    # First addition
    SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach',
        proficiency='intermediate'
    )

    # Second addition attempt via HTTP
    response = auth_client.post('/skills/add', data={
        'skill_id': sample_skill.id,
        'skill_type': 'teach',
        'proficiency': 'advanced',
        'notes': 'Trying duplicate'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "already have &#39;Python&#39; in your teach skills list" in html or "already have 'Python' in your teach skills list" in html

    # Verify only 1 record exists in DB
    count = UserSkill.query.filter_by(user_id=student_user.id, skill_id=sample_skill.id).count()
    assert count == 1

def test_prevent_adding_same_skill_as_both_teach_and_learn(auth_client, student_user, sample_skill):
    """A student cannot add a skill to Learn if they already teach it (mutual exclusivity)."""
    # Student already teaches Python
    SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach',
        proficiency='advanced'
    )

    # Attempt to add Python to learn
    response = auth_client.post('/skills/add', data={
        'skill_id': sample_skill.id,
        'skill_type': 'learn',
        'proficiency': 'beginner',
        'notes': 'Cannot both teach and learn same skill'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "cannot be added to both Teach and Learn simultaneously" in html

    # Verify only the teach record remains
    learn_record = UserSkill.query.filter_by(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='learn'
    ).first()
    assert learn_record is None

def test_edit_skill_proficiency_and_notes(auth_client, student_user, sample_skill):
    """Student can edit the proficiency level and notes of their skill."""
    user_skill, _ = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach',
        proficiency='intermediate',
        notes='Old notes'
    )

    response = auth_client.post(f'/skills/edit/{user_skill.id}', data={
        'proficiency': 'advanced',
        'notes': 'Updated notes: specialized in Pandas and NumPy'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Updated &#39;Python&#39; details successfully." in html or "Updated 'Python' details successfully." in html

    updated = db.session.get(UserSkill, user_skill.id)
    assert updated.proficiency == 'advanced'
    assert updated.notes == 'Updated notes: specialized in Pandas and NumPy'

def test_delete_skill_from_portfolio(auth_client, student_user, sample_skill):
    """Student can delete a skill from their portfolio."""
    user_skill, _ = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach',
        proficiency='intermediate'
    )

    response = auth_client.post(f'/skills/delete/{user_skill.id}', follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Removed &#39;Python&#39; from your teach list." in html or "Removed 'Python' from your teach list." in html

    # Record should no longer exist
    deleted = db.session.get(UserSkill, user_skill.id)
    assert deleted is None

def test_prevent_unauthorized_user_from_editing_other_student_skill(client, second_student_user, student_user, sample_skill):
    """Student B cannot edit Student A's skill."""
    # Student A's skill
    user_skill, _ = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach',
        proficiency='intermediate'
    )

    # Login as Student B
    client.post('/auth/login', data={
        'email': 'priya@college.edu',
        'password': 'priyaPassword456'
    }, follow_redirects=True)

    # Student B attempts to edit Student A's skill
    response = client.post(f'/skills/edit/{user_skill.id}', data={
        'proficiency': 'beginner',
        'notes': 'Malicious modification attempt'
    })

    assert response.status_code == 403

    # Check database was not modified
    skill_in_db = db.session.get(UserSkill, user_skill.id)
    assert skill_in_db.proficiency == 'intermediate'

def test_prevent_unauthorized_user_from_deleting_other_student_skill(client, second_student_user, student_user, sample_skill):
    """Student B cannot delete Student A's skill."""
    # Student A's skill
    user_skill, _ = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach',
        proficiency='intermediate'
    )

    # Login as Student B
    client.post('/auth/login', data={
        'email': 'priya@college.edu',
        'password': 'priyaPassword456'
    }, follow_redirects=True)

    # Student B attempts to delete Student A's skill
    response = client.post(f'/skills/delete/{user_skill.id}')
    assert response.status_code == 403

    # Check skill still exists in database
    skill_in_db = db.session.get(UserSkill, user_skill.id)
    assert skill_in_db is not None

def test_admin_can_create_category(admin_client):
    """Admin can create a new skill category."""
    response = admin_client.post('/admin/categories/add', data={
        'name': 'Cloud Computing & DevOps',
        'icon': 'bi-cloud-arrow-up',
        'description': 'Infrastructure, containerization, and cloud deployment'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Category &#39;Cloud Computing &amp; DevOps&#39; created successfully." in html or "Cloud Computing & DevOps" in html

    cat = SkillCategory.query.filter_by(name='Cloud Computing & DevOps').first()
    assert cat is not None
    assert cat.icon == 'bi-cloud-arrow-up'

def test_admin_can_create_skill(admin_client, sample_category):
    """Admin can create a new standardized skill."""
    response = admin_client.post('/admin/skills/add', data={
        'category_id': sample_category.id,
        'name': 'Rust',
        'description': 'Memory-safe systems programming'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Skill &#39;Rust&#39; added to category" in html or "Rust" in html

    skill = Skill.query.filter_by(name='Rust').first()
    assert skill is not None
    assert skill.category_id == sample_category.id

def test_student_cannot_access_admin_skill_routes(auth_client, sample_category):
    """Regular student cannot create categories or skills via admin endpoints (RBAC)."""
    cat_response = auth_client.post('/admin/categories/add', data={
        'name': 'Hacking Category',
        'icon': 'bi-bug',
        'description': 'Unauthorized'
    })
    assert cat_response.status_code == 403

    skill_response = auth_client.post('/admin/skills/add', data={
        'category_id': sample_category.id,
        'name': 'Unauthorized Skill',
        'description': 'Unauthorized'
    })
    assert skill_response.status_code == 403

def test_cli_seed_skills_command(cli_runner):
    """The CLI seed-skills command idempotently populates standard categories and skills."""
    result = cli_runner.invoke(args=['seed-skills'])
    assert result.exit_code == 0
    assert "[SUCCESS] Skills seeding complete" in result.output

    # Verify categories and skills exist
    python_skill = Skill.query.filter_by(name='Python').first()
    assert python_skill is not None
    assert python_skill.category.name == 'Programming Languages'

    # Running a second time should not duplicate
    result_second = cli_runner.invoke(args=['seed-skills'])
    assert result_second.exit_code == 0
    assert "0 categories added, 0 skills added" in result_second.output

def test_explore_skills_catalog_public(client, sample_category, sample_skill):
    """Explore skills catalog is accessible publicly and lists categories."""
    response = client.get('/skills/explore')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Academic &amp; Professional Skill Catalog" in html or "Academic & Professional Skill Catalog" in html
    assert "Programming Languages" in html
    assert "Python" in html
