"""
Admin Blueprint routes: Protected Admin Portal guarded by role-based authorization.
Includes Category and Standard Skill management.
"""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.forms.skill_forms import CategoryForm, AdminSkillForm
from app.models.skill import SkillCategory, Skill
from app.services.skill_service import SkillService

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to restrict access to administrator accounts only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('')
@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with category and skill management."""
    category_form = CategoryForm()
    skill_form = AdminSkillForm()
    
    categories = SkillCategory.query.order_by(SkillCategory.name.asc()).all()
    skills = Skill.query.order_by(Skill.name.asc()).all()
    
    skill_form.category_id.choices = [(c.id, c.name) for c in categories]
    
    return render_template(
        'admin/dashboard.html',
        categories=categories,
        skills=skills,
        category_form=category_form,
        skill_form=skill_form
    )

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    """Create a new skill category."""
    form = CategoryForm()
    if form.validate_on_submit():
        category, error = SkillService.create_category(
            name=form.name.data,
            description=form.description.data,
            icon=form.icon.data
        )
        if error:
            flash(error, 'danger')
        else:
            flash(f"Category '{category.name}' created successfully.", 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Category error: {error}", 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/skills/add', methods=['POST'])
@login_required
@admin_required
def add_skill():
    """Create a new standardized skill."""
    form = AdminSkillForm()
    categories = SkillCategory.query.order_by(SkillCategory.name.asc()).all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        skill, error = SkillService.create_skill(
            category_id=form.category_id.data,
            name=form.name.data,
            description=form.description.data
        )
        if error:
            flash(error, 'danger')
        else:
            flash(f"Skill '{skill.name}' added to category '{skill.category.name}'.", 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Skill error: {error}", 'danger')
    return redirect(url_for('admin.dashboard'))
