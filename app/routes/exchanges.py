"""
Exchanges Blueprint routes: Requests lifecycle, Session scheduling, and History.
"""
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.forms.exchange_forms import CreateExchangeRequestForm, ScheduleSessionForm
from app.forms.review_forms import RatingForm
from app.models.user import User
from app.models.skill import Skill
from app.models.exchange import ExchangeRequest, ExchangeSession
from app.services.exchange_service import ExchangeService
from app.services.rating_service import RatingService

exchanges_bp = Blueprint('exchanges', __name__, url_prefix='/exchanges')

@exchanges_bp.route('/')
@login_required
def index():
    """List student's incoming and outgoing exchange requests with status overview."""
    tab = request.args.get('tab', 'incoming')
    requests_data = ExchangeService.get_user_requests(current_user.id)
    return render_template(
        'exchanges/index.html',
        incoming=requests_data['incoming'],
        outgoing=requests_data['outgoing'],
        active_tab=tab
    )

@exchanges_bp.route('/<int:request_id>')
@login_required
def request_detail(request_id: int):
    """View details of a specific exchange request."""
    req = db.session.get(ExchangeRequest, request_id)
    if not req or not req.is_participant(current_user.id):
        abort(404)

    is_sender = (req.sender_id == current_user.id)
    partner = req.partner(current_user.id)

    return render_template(
        'exchanges/request_detail.html',
        req=req,
        is_sender=is_sender,
        partner=partner
    )

@exchanges_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_request():
    """Form to initiate a new skill exchange proposal."""
    receiver_id = request.args.get('receiver_id', type=int)
    pre_offered_id = request.args.get('offered_id', type=int)
    pre_requested_id = request.args.get('requested_id', type=int)

    if not receiver_id:
        flash("Please select a student peer to send an exchange request.", "info")
        return redirect(url_for('matching.index'))

    if receiver_id == current_user.id:
        flash("You cannot send an exchange request to yourself.", "warning")
        return redirect(url_for('matching.index'))

    target_user = User.query.filter_by(id=receiver_id, role='student').first_or_404()

    form = CreateExchangeRequestForm()
    form.receiver_id.data = str(receiver_id)

    # Populate offered skills: current user's teach skills
    user_teach = current_user.teach_skills
    if not user_teach:
        flash("You need to add at least one 'Teach' skill to your portfolio before sending an exchange request.", "warning")
        return redirect(url_for('skills.index'))

    form.offered_skill_id.choices = [
        (us.skill.id, f"{us.skill.name} ({us.proficiency.capitalize()})")
        for us in user_teach
    ]

    # Populate requested skills: target user's teach skills
    target_teach = target_user.teach_skills
    if not target_teach:
        flash(f"{target_user.name} has not listed any skills to teach yet.", "warning")
        return redirect(url_for('matching.student_detail', user_id=target_user.id))

    form.requested_skill_id.choices = [
        (us.skill.id, f"{us.skill.name} ({us.proficiency.capitalize()})")
        for us in target_teach
    ]

    # Pre-select if passed via query params and valid
    if request.method == 'GET':
        if pre_offered_id and pre_offered_id in [c[0] for c in form.offered_skill_id.choices]:
            form.offered_skill_id.data = pre_offered_id
        if pre_requested_id and pre_requested_id in [c[0] for c in form.requested_skill_id.choices]:
            form.requested_skill_id.data = pre_requested_id

    if form.validate_on_submit():
        req, error = ExchangeService.create_request(
            sender_id=current_user.id,
            receiver_id=int(form.receiver_id.data),
            offered_skill_id=form.offered_skill_id.data,
            requested_skill_id=form.requested_skill_id.data,
            message=form.message.data
        )
        if error:
            flash(error, 'danger')
        else:
            flash(f"Exchange request successfully sent to {target_user.name}!", 'success')
            return redirect(url_for('exchanges.request_detail', request_id=req.id))

    return render_template(
        'exchanges/new_request.html',
        form=form,
        target_user=target_user
    )

@exchanges_bp.route('/respond/<int:request_id>/<action>', methods=['POST'])
@login_required
def respond_request(request_id: int, action: str):
    """Accept or reject an incoming request."""
    success, error = ExchangeService.respond_to_request(
        request_id=request_id,
        user_id=current_user.id,
        action=action
    )
    if success:
        flash(f"Exchange request {action}ed successfully.", 'success')
    else:
        flash(error or 'Failed to process request.', 'danger')

    return redirect(url_for('exchanges.request_detail', request_id=request_id))

@exchanges_bp.route('/cancel/<int:request_id>', methods=['POST'])
@login_required
def cancel_request(request_id: int):
    """Cancel an outgoing pending request."""
    success, error = ExchangeService.cancel_request(
        request_id=request_id,
        user_id=current_user.id
    )
    if success:
        flash("Exchange request cancelled.", 'info')
    else:
        flash(error or 'Failed to cancel request.', 'danger')

    return redirect(url_for('exchanges.request_detail', request_id=request_id))

@exchanges_bp.route('/schedule/<int:request_id>', methods=['GET', 'POST'])
@login_required
def schedule_session(request_id: int):
    """Schedule or reschedule a learning session for an accepted request."""
    req = db.session.get(ExchangeRequest, request_id)
    if not req or not req.is_participant(current_user.id):
        abort(404)

    if req.status != 'accepted':
        flash("A session can only be scheduled for an accepted exchange request.", "warning")
        return redirect(url_for('exchanges.request_detail', request_id=req.id))

    if req.session and req.session.status == 'scheduled':
        flash("A session is already scheduled for this exchange.", "info")
        return redirect(url_for('exchanges.session_detail', session_id=req.session.id))

    if req.session and req.session.status == 'completed':
        flash("This exchange session has already been completed.", "info")
        return redirect(url_for('exchanges.session_detail', session_id=req.session.id))

    form = ScheduleSessionForm()
    form.request_id.data = str(req.id)

    # Pre-populate defaults if rescheduling a cancelled session
    if request.method == 'GET' and req.session and req.session.status == 'cancelled':
        form.duration_minutes.data = req.session.duration_minutes
        form.mode.data = req.session.mode
        form.meeting_details.data = req.session.meeting_details
        form.notes.data = req.session.notes

    if form.validate_on_submit():
        combined_dt = datetime.combine(form.scheduled_date.data, form.scheduled_time.data)
        session, error = ExchangeService.schedule_session(
            request_id=req.id,
            user_id=current_user.id,
            scheduled_at=combined_dt,
            duration_minutes=form.duration_minutes.data,
            mode=form.mode.data,
            meeting_details=form.meeting_details.data,
            notes=form.notes.data
        )
        if error:
            flash(error, 'danger')
        else:
            flash("Learning session successfully scheduled!", 'success')
            return redirect(url_for('exchanges.session_detail', session_id=session.id))

    partner = req.partner(current_user.id)
    return render_template(
        'exchanges/schedule_session.html',
        form=form,
        req=req,
        partner=partner
    )

@exchanges_bp.route('/sessions')
@login_required
def sessions_list():
    """List all scheduled and historical exchange sessions."""
    sessions_data = ExchangeService.get_user_sessions(current_user.id)
    return render_template(
        'exchanges/sessions.html',
        upcoming_sessions=sessions_data['upcoming'],
        past_sessions=sessions_data['past']
    )

@exchanges_bp.route('/sessions/<int:session_id>')
@login_required
def session_detail(session_id: int):
    """View details of a specific session."""
    sess = db.session.get(ExchangeSession, session_id)
    if not sess or not sess.is_participant(current_user.id):
        abort(404)

    partner = sess.partner(current_user.id)
    my_rating = sess.get_user_rating(current_user.id)
    partner_rating = sess.get_partner_rating(current_user.id)

    return render_template(
        'exchanges/session_detail.html',
        session=sess,
        partner=partner,
        my_rating=my_rating,
        partner_rating=partner_rating
    )

@exchanges_bp.route('/sessions/<int:session_id>/complete', methods=['POST'])
@login_required
def complete_session(session_id: int):
    """Mark a scheduled session as completed."""
    success, error = ExchangeService.complete_session(
        session_id=session_id,
        user_id=current_user.id
    )
    if success:
        flash("Session marked as completed! Knowledge exchange complete.", 'success')
    else:
        flash(error or 'Failed to update session.', 'danger')

    return redirect(url_for('exchanges.session_detail', session_id=session_id))

@exchanges_bp.route('/sessions/<int:session_id>/cancel', methods=['POST'])
@login_required
def cancel_session(session_id: int):
    """Cancel a scheduled session."""
    success, error = ExchangeService.cancel_session(
        session_id=session_id,
        user_id=current_user.id
    )
    if success:
        flash("Session cancelled.", 'info')
    else:
        flash(error or 'Failed to cancel session.', 'danger')

    return redirect(url_for('exchanges.session_detail', session_id=session_id))

@exchanges_bp.route('/sessions/<int:session_id>/rate', methods=['GET', 'POST'])
@login_required
def rate_session(session_id: int):
    """Submit post-session rating and qualitative feedback."""
    sess = db.session.get(ExchangeSession, session_id)
    if not sess or not sess.is_participant(current_user.id):
        abort(404)

    if not sess.is_completed:
        flash("You can only rate a session that has been marked as Completed.", "warning")
        return redirect(url_for('exchanges.session_detail', session_id=sess.id))

    if sess.has_user_rated(current_user.id):
        flash("You have already submitted your rating and review for this session.", "info")
        return redirect(url_for('exchanges.session_detail', session_id=sess.id))

    partner = sess.partner(current_user.id)
    form = RatingForm()

    if form.validate_on_submit():
        rating, error = RatingService.submit_rating(
            session_id=sess.id,
            reviewer_id=current_user.id,
            score=form.score.data,
            feedback=form.feedback.data
        )
        if error:
            flash(error, 'danger')
        else:
            flash(f"Thank you! Your rating and feedback for {partner.name} have been submitted.", 'success')
            return redirect(url_for('exchanges.session_detail', session_id=sess.id))

    return render_template(
        'exchanges/rate_session.html',
        form=form,
        session=sess,
        partner=partner
    )

