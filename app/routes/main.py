"""
Main Blueprint routes: Landing, Dashboard, and Profile.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.forms.auth_forms import ProfileForm
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.stats_service import StatsService
from app.services.rating_service import RatingService

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Public landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Personalized student dashboard backed by real SQLite database statistics
    and Chart.js visualizations.
    """
    stats = StatsService.get_student_dashboard_stats(current_user)
    return render_template(
        'main/dashboard.html',
        stats=stats,
        chart_data=stats['chart_data']
    )

@main_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update logged-in user's profile and inspect received peer reviews."""
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        success, error = AuthService.update_profile(
            user=current_user,
            name=form.name.data,
            college=form.college.data,
            bio=form.bio.data,
            availability=form.availability.data
        )
        if success:
            flash('Your profile has been updated successfully.', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash(error or 'Failed to update profile.', 'danger')

    reviews = RatingService.get_user_received_ratings(current_user.id)
    return render_template(
        'main/profile.html',
        form=form,
        user=current_user,
        reviews=reviews
    )
