"""
Authentication Blueprint routes: Registration, Login, Logout.
"""
from urllib.parse import urlsplit
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.auth_forms import LoginForm, RegisterForm
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new student account."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        user, error = AuthService.register_user(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            college=form.college.data,
            bio=form.bio.data,
            availability=form.availability.data,
            role='student'
        )
        if error:
            flash(error, 'danger')
        else:
            flash('Your account has been created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Authenticate and log in an existing user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = AuthService.authenticate(
            email=form.email.data,
            password=form.password.data
        )
        if user:
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.name}!", "success")
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email or password. Please check your credentials.', 'danger')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out securely.', 'info')
    return redirect(url_for('main.index'))
