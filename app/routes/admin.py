"""
Admin Blueprint routes: Protected Admin Portal guarded by role-based authorization.
Includes Category and Standard Skill management, Student Moderation, and Platform Monitoring.
"""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from app.forms.skill_forms import CategoryForm, AdminSkillForm
from app.models.skill import SkillCategory, Skill
from app.models.user import User
from app.models.exchange import ExchangeRequest, ExchangeSession
from app.services.skill_service import SkillService
from app.services.auth_service import AuthService
from app.services.stats_service import StatsService

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
    """Admin dashboard with category, skill, student moderation, and monitoring metrics."""
    category_form = CategoryForm()
    skill_form = AdminSkillForm()
    
    categories = SkillCategory.query.order_by(SkillCategory.name.asc()).all()
    skills = Skill.query.order_by(Skill.name.asc()).all()
    skill_form.category_id.choices = [(c.id, c.name) for c in categories]

    # Student moderation query with optional search
    search_q = request.args.get('q', '').strip()
    student_query = User.query.filter_by(role='student')
    if search_q:
        clean_q = f"%{search_q.lower()}%"
        student_query = student_query.filter(
            (User.name.ilike(clean_q)) |
            (User.email.ilike(clean_q)) |
            (User.college.ilike(clean_q))
        )
    students = student_query.order_by(User.created_at.desc()).all()

    # Aggregate comprehensive platform metrics
    stats = StatsService.get_admin_stats()

    # Recent platform activities for monitoring
    recent_requests = ExchangeRequest.query.order_by(ExchangeRequest.created_at.desc()).limit(6).all()
    recent_sessions = ExchangeSession.query.order_by(ExchangeSession.created_at.desc()).limit(6).all()

    return render_template(
        'admin/dashboard.html',
        categories=categories,
        skills=skills,
        students=students,
        stats=stats,
        chart_data=stats.get('chart_data', {}),
        recent_requests=recent_requests,
        recent_sessions=recent_sessions,
        category_form=category_form,
        skill_form=skill_form,
        search_q=search_q
    )

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(user_id: int):
    """Delete a suspicious or fraudulent student account."""
    success, message = AuthService.delete_student(user_id=user_id, current_admin_id=current_user.id)
    if success:
        flash(message, 'success')
    else:
        flash(message or 'Failed to delete student.', 'danger')
    return redirect(url_for('admin.dashboard'))

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

@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_category(category_id: int):
    """Delete a skill category."""
    success, message = SkillService.delete_category(category_id)
    if success:
        flash(message, 'success')
    else:
        flash(message or 'Failed to delete category.', 'danger')
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

@admin_bp.route('/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_skill(skill_id: int):
    """Delete a standardized skill from taxonomy."""
    success, message = SkillService.delete_standard_skill(skill_id)
    if success:
        flash(message, 'success')
    else:
        flash(message or 'Failed to delete skill.', 'danger')
    return redirect(url_for('admin.dashboard'))

