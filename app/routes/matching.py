"""
Matching Blueprint routes: Recommendations, student discovery, and peer profile inspection.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.models.skill import SkillCategory, Skill
from app.services.matching_service import MatchingService
from app.services.skill_service import SkillService

matching_bp = Blueprint('matching', __name__, url_prefix='/matching')

@matching_bp.route('/')
@login_required
def index():
    """Display compatible skill partner recommendations for the logged in student."""
    filter_reciprocal = request.args.get('reciprocal', '0') == '1'
    all_matches = MatchingService.get_matches_for_user(current_user)

    if filter_reciprocal:
        matches = [m for m in all_matches if m['is_reciprocal']]
    else:
        matches = all_matches

    return render_template(
        'matching/index.html',
        matches=matches,
        total_matches=len(all_matches),
        filter_reciprocal=filter_reciprocal
    )

@matching_bp.route('/discover')
@login_required
def discover():
    """Search and discover fellow students by skill, category, and proficiency."""
    query = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)
    proficiency = request.args.get('proficiency', '').strip().lower()
    intent = request.args.get('intent', 'all').strip().lower()

    categories = SkillCategory.query.order_by(SkillCategory.name.asc()).all()

    students = SkillService.search_students(
        current_user_id=current_user.id,
        query=query if query else None,
        category_id=category_id if category_id and category_id > 0 else None,
        proficiency=proficiency if proficiency else None,
        intent=intent
    )

    return render_template(
        'matching/discover.html',
        students=students,
        categories=categories,
        query=query,
        selected_category=category_id or 0,
        selected_proficiency=proficiency,
        selected_intent=intent
    )

@matching_bp.route('/student/<int:user_id>')
@login_required
def student_detail(user_id: int):
    """View public student profile and compatibility breakdown relative to the current user."""
    student = User.query.filter_by(id=user_id, role='student').first_or_404()

    # Calculate compatibility if not self
    match_data = None
    if student.id != current_user.id:
        match_data = MatchingService.calculate_compatibility(current_user, student)

    return render_template(
        'matching/student_detail.html',
        student=student,
        match=match_data
    )
