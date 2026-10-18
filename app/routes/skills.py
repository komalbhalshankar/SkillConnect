"""
Skills Blueprint routes: Manage personal skill portfolio (Add, Edit, Delete)
and browse categorized skill catalog.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.forms.skill_forms import AddUserSkillForm, EditUserSkillForm
from app.models.skill import Skill, SkillCategory, UserSkill
from app.services.skill_service import SkillService
from app.extensions import db

skills_bp = Blueprint('skills', __name__, url_prefix='/skills')

@skills_bp.route('/', methods=['GET'])
@login_required
def index():
    """Display student's current Teach and Learn skills with add form."""
    form = AddUserSkillForm()
    categories = SkillCategory.query.order_by(SkillCategory.name.asc()).all()
    skills = Skill.query.order_by(Skill.name.asc()).all()

    form.skill_id.choices = [(0, "-- Select an existing skill --")] + [
        (s.id, f"{s.name} ({s.category.name})") for s in skills
    ]
    form.category_id.choices = [(0, "-- Select Category (for new skill) --")] + [
        (c.id, c.name) for c in categories
    ]

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
    """Add an existing or new skill to current student's portfolio."""
    form = AddUserSkillForm()
    skills = Skill.query.order_by(Skill.name.asc()).all()
    categories = SkillCategory.query.order_by(SkillCategory.name.asc()).all()

    form.skill_id.choices = [(0, "-- Select an existing skill --")] + [
        (s.id, f"{s.name} ({s.category.name})") for s in skills
    ]
    form.category_id.choices = [(0, "-- Select Category (for new skill) --")] + [
        (c.id, c.name) for c in categories
    ]

    # Handle skill selection or custom addition
    selected_skill_id = form.skill_id.data if form.skill_id.data and form.skill_id.data > 0 else None
    custom_name = form.custom_skill_name.data.strip() if form.custom_skill_name.data else None
    selected_cat_id = form.category_id.data if form.category_id.data and form.category_id.data > 0 else None

    if not selected_skill_id and not custom_name:
        flash("Please select an existing skill or enter a new skill name.", "danger")
        return redirect(url_for('skills.index'))

    skill_type = form.skill_type.data or 'teach'
    proficiency = form.proficiency.data or 'intermediate'
    notes = form.notes.data

    user_skill, error = SkillService.add_user_skill(
        user_id=current_user.id,
        skill_id=selected_skill_id,
        skill_type=skill_type,
        proficiency=proficiency,
        notes=notes,
        custom_skill_name=custom_name,
        category_id=selected_cat_id
    )

    if error:
        flash(error, 'danger')
    else:
        flash(f"Successfully added '{user_skill.skill.name}' to your {user_skill.skill_type.upper()} list!", 'success')

    return redirect(url_for('skills.index'))

@skills_bp.route('/edit/<int:user_skill_id>', methods=['POST'])
@login_required
def edit(user_skill_id: int):
    """Edit skill type, proficiency level and notes of a student's skill."""
    user_skill = db.session.get(UserSkill, user_skill_id)
    if not user_skill:
        flash('Skill record not found.', 'danger')
        return redirect(url_for('skills.index'))

    # Strict ownership enforcement
    if user_skill.user_id != current_user.id:
        abort(403)

    skill_type = request.form.get('skill_type', user_skill.skill_type)
    proficiency = request.form.get('proficiency', user_skill.proficiency)
    notes = request.form.get('notes', user_skill.notes)

    success, error = SkillService.update_user_skill(
        user_skill_id=user_skill_id,
        user_id=current_user.id,
        proficiency=proficiency,
        notes=notes,
        skill_type=skill_type
    )

    if success:
        flash(f"Updated '{user_skill.skill.name}' details successfully.", 'success')
    else:
        flash(error or 'Failed to update skill.', 'danger')

    return redirect(url_for('skills.index'))

@skills_bp.route('/delete/<int:user_skill_id>', methods=['POST'])
@login_required
def delete(user_skill_id: int):
    """Remove a skill from current student's portfolio."""
    user_skill = db.session.get(UserSkill, user_skill_id)
    if not user_skill:
        flash('Skill record not found.', 'danger')
        return redirect(url_for('skills.index'))

    # Strict ownership enforcement
    if user_skill.user_id != current_user.id:
        abort(403)

    skill_name = user_skill.skill.name
    skill_type = user_skill.skill_type
    success, error = SkillService.delete_user_skill(
        user_skill_id=user_skill_id,
        user_id=current_user.id
    )
    if success:
        flash(f"Removed '{skill_name}' from your {skill_type.upper()} list.", 'info')
    else:
        flash(error or 'Failed to delete skill.', 'danger')

    return redirect(url_for('skills.index'))

@skills_bp.route('/explore', methods=['GET'])
def explore():
    """Public/student view of all skill categories and skills."""
    categories = SkillCategory.query.order_by(SkillCategory.name.asc()).all()
    return render_template('skills/explore.html', categories=categories)
