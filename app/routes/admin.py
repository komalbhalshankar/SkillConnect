"""
Admin Blueprint routes: Protected Admin Portal guarded by role-based authorization.
"""
from functools import wraps
from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

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
    """Admin dashboard placeholder verifying administrative role access."""
    return render_template('admin/dashboard.html')
