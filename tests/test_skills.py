"""
Unit and integration tests for Skill Management (Phase 3 Module 2).
Tests skill catalog taxonomy, student skill portfolio (Teach & Learn),
unlisted skill addition without uncontrolled duplicates, skill editing,
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
    assert "Successfully added" in html
    assert "Python" in html

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
    assert "Successfully added" in html
    assert "Java" in html

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
    assert "already have" in html.lower()

    # Verify only 1 record exists in DB for this skill_type
    count = UserSkill.query.filter_by(user_id=student_user.id, skill_id=sample_skill.id, skill_type='teach').count()
    assert count == 1

def test_associate_same_skill_with_both_teach_and_learn(auth_client, student_user, sample_skill):
    """A student can associate the same skill with both TEACH and LEARN with distinct proficiencies."""
    # Add Python as TEACH (Advanced)
    user_skill_teach, err1 = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach',
        proficiency='advanced',
        notes='Can teach fundamentals and scripting'
    )
    assert err1 is None
    assert user_skill_teach is not None

    # Add Python as LEARN (Beginner/Target)
    user_skill_learn, err2 = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='learn',
        proficiency='beginner',
        notes='Want to learn advanced internals and async'
    )
    assert err2 is None
    assert user_skill_learn is not None

    # Verify both records exist under the same user
    teach_count = UserSkill.query.filter_by(user_id=student_user.id, skill_id=sample_skill.id, skill_type='teach').count()
    learn_count = UserSkill.query.filter_by(user_id=student_user.id, skill_id=sample_skill.id, skill_type='learn').count()
    assert teach_count == 1
    assert learn_count == 1

def test_add_custom_unlisted_skill_creates_standard_skill(auth_client, student_user, sample_category):
    """Student can add an unlisted custom skill; it is created under the chosen category without error."""
    response = auth_client.post('/skills/add', data={
        'skill_id': 0,
        'custom_skill_name': 'Solidity',
        'category_id': sample_category.id,
        'skill_type': 'learn',
        'proficiency': 'beginner',
        'notes': 'Smart contract programming'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Successfully added" in html
    assert "Solidity" in html

    # Check Skill was created
    new_skill = Skill.query.filter_by(name='Solidity').first()
    assert new_skill is not None
    assert new_skill.category_id == sample_category.id

    # Check UserSkill was linked
    user_skill = UserSkill.query.filter_by(user_id=student_user.id, skill_id=new_skill.id).first()
    assert user_skill is not None
    assert user_skill.skill_type == 'learn'

def test_add_custom_skill_reuses_existing_skill_case_insensitively(auth_client, student_user, sample_skill):
    """Entering an unlisted skill whose name already exists reuses the existing record without duplicate creation."""
    initial_skill_count = Skill.query.count()

    # Enter 'python' in lowercase
    response = auth_client.post('/skills/add', data={
        'skill_id': 0,
        'custom_skill_name': 'python',
        'category_id': sample_skill.category_id,
        'skill_type': 'teach',
        'proficiency': 'intermediate'
    }, follow_redirects=True)

    assert response.status_code == 200
    # Skill count in database must NOT have increased
    assert Skill.query.count() == initial_skill_count

    # UserSkill must link to the existing sample_skill ID
    user_skill = UserSkill.query.filter_by(user_id=student_user.id, skill_id=sample_skill.id).first()
    assert user_skill is not None

def test_edit_skill_type_and_proficiency(auth_client, student_user, sample_skill):
    """Student can edit the skill type, proficiency level, and notes of their skill."""
    user_skill, _ = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach',
        proficiency='intermediate',
        notes='Old notes'
    )

    response = auth_client.post(f'/skills/edit/{user_skill.id}', data={
        'skill_type': 'learn',
        'proficiency': 'advanced',
        'notes': 'Switched to learn and updated notes'
    }, follow_redirects=True)

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Updated" in html

    updated = db.session.get(UserSkill, user_skill.id)
    assert updated.skill_type == 'learn'
    assert updated.proficiency == 'advanced'
    assert updated.notes == 'Switched to learn and updated notes'

def test_reject_invalid_proficiency_or_skill_type(student_user, sample_skill):
    """Service strictly rejects invalid proficiency and skill type strings."""
    _, err_type = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='invalid_type'
    )
    assert "Invalid skill type" in err_type

    user_skill, _ = SkillService.add_user_skill(
        user_id=student_user.id,
        skill_id=sample_skill.id,
        skill_type='teach'
    )
    success, err_prof = SkillService.update_user_skill(
        user_skill_id=user_skill.id,
        user_id=student_user.id,
        proficiency='expert_ninja'
    )
    assert success is False
    assert "Invalid proficiency" in err_prof

def test_handle_nonexistent_skill_safely(auth_client):
    """Submitting a nonexistent skill ID returns user-friendly error without crashing."""
    response = auth_client.post('/skills/add', data={
        'skill_id': 99999,
        'skill_type': 'teach',
        'proficiency': 'beginner'
    }, follow_redirects=True)
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Selected skill does not exist" in html or "error" in html.lower()

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
    assert "Removed" in html

    # Record should no longer exist
    deleted = db.session.get(UserSkill, user_skill.id)
    assert deleted is None

def test_prevent_unauthorized_user_from_editing_other_student_skill(client, second_student_user, student_user, sample_skill):
    """Student B cannot edit Student A's skill."""
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
        'skill_type': 'teach',
        'proficiency': 'beginner',
        'notes': 'Malicious modification attempt'
    })
    assert response.status_code == 403

    # Check database was not modified
    skill_in_db = db.session.get(UserSkill, user_skill.id)
    assert skill_in_db.proficiency == 'intermediate'

def test_prevent_unauthorized_user_from_deleting_other_student_skill(client, second_student_user, student_user, sample_skill):
    """Student B cannot delete Student A's skill."""
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
    assert "Cloud Computing &amp; DevOps" in html or "Cloud Computing & DevOps" in html

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
    assert "Rust" in html

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
    assert python_skill.category.name == 'Programming'

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
    assert "Programming" in html
    assert "Python" in html
