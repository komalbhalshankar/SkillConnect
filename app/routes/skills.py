"""
Skills Blueprint routes: Manage personal skill portfolio (Add, Edit, Delete).
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.forms.skill_forms import AddUserSkillForm, EditUserSkillForm
from app.models.skill import Skill, SkillCategory, UserSkill
from app.services.skill_service import SkillService

skills_bp = Blueprint('skills', __name__, url_prefix='/skills')

@skills_bp.route('/', methods=['GET'])
@login_required
def index():
    """Display student's current Teach and Learn skills with add form."""
    form = AddUserSkillForm()
    # Populate skill choices ordered by Category and Skill Name
    categories = SkillCategory.query.order_by(SkillCategory.name.asc()).all()
    skills = Skill.query.order_by(Skill.name.asc()).all()
    form.skill_id.choices = [(s.id, f"{s.name} ({s.category.name})") for s in skills]

    teach_skills = SkillService.get_user_skills(current_user.id, skill_type='teach')
    learn_skills = SkillService.get_user_skills(current_user.id, skill_type='learn')

    return render_template(
        'skills/index.html',
        form=form,
        teach_skills=teach_skills,
        learn_skills=learn_skills,
        categories=categories
    )

@skills_bp.route('/add', methods=['POST'])
@login_required
def add():
    """Add a skill to current student's portfolio."""
    form = AddUserSkillForm()
    skills = Skill.query.order_by(Skill.name.asc()).all()
    form.skill_id.choices = [(s.id, f"{s.name} ({s.category.name})") for s in skills]

    if form.validate_on_submit():
        user_skill, error = SkillService.add_user_skill(
            user_id=current_user.id,
            skill_id=form.skill_id.data,
            skill_type=form.skill_type.data,
            proficiency=form.proficiency.data,
            notes=form.notes.data
        )
        if error:
            flash(error, 'danger')
        else:
            flash(f"Successfully added '{user_skill.skill.name}' to your {user_skill.skill_type} list!", 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", 'danger')

    return redirect(url_for('skills.index'))

@skills_bp.route('/edit/<int:user_skill_id>', methods=['POST'])
@login_required
def edit(user_skill_id: int):
    """Edit proficiency level and notes of a student's skill."""
    form = EditUserSkillForm()
    if form.validate_on_submit():
        success, error = SkillService.update_user_skill(
            user_skill_id=user_skill_id,
            user_id=current_user.id,
            proficiency=form.proficiency.data,
            notes=form.notes.data
        )
        if success:
            flash('Skill details updated successfully.', 'success')
        else:
            flash(error or 'Failed to update skill.', 'danger')
    else:
        flash('Invalid submission data.', 'danger')

    return redirect(url_for('skills.index'))

@skills_bp.route('/delete/<int:user_skill_id>', methods=['POST'])
@login_required
def delete(user_skill_id: int):
    """Remove a skill from current student's portfolio."""
    success, error = SkillService.delete_user_skill(
        user_skill_id=user_skill_id,
        user_id=current_user.id
    )
    if success:
        flash('Skill removed from your portfolio.', 'info')
    else:
        flash(error or 'Failed to delete skill.', 'danger')

    return redirect(url_for('skills.index'))
