"""
Matching Blueprint routes: Recommendations, partner discovery, and score breakdown.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.services.matching_service import MatchingService

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

@matching_bp.route('/breakdown/<int:candidate_id>')
@login_required
def breakdown(candidate_id: int):
    """Inspect detailed transparent formula breakdown for a specific candidate."""
    if candidate_id == current_user.id:
        flash("You cannot match with yourself.", "warning")
        return redirect(url_for('matching.index'))

    candidate = User.query.filter_by(id=candidate_id, role='student').first_or_404()
    match_data = MatchingService.calculate_compatibility(current_user, candidate)

    return render_template(
        'matching/breakdown.html',
        candidate=candidate,
        match=match_data
    )
