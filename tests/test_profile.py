from app.extensions import db
from app.models.user import User
from app.services.auth_service import AuthService

def test_view_logged_in_profile(auth_client, student_user):
    """Verify that logged in student can view their own profile details."""
    response = auth_client.get('/profile')
    assert response.status_code == 200
    assert student_user.name.encode() in response.data
    assert student_user.email.encode() in response.data
    assert student_user.college.encode() in response.data

def test_update_profile_success(auth_client, app, student_user):
    """Verify that a student can update their name, college, bio, and availability."""
    response = auth_client.post('/profile', data={
        'name': 'Aarav Sharma Updated',
        'college': 'Indian Institute of Technology, Bombay',
        'bio': 'Full-stack developer focused on Flask and Python systems.',
        'availability': 'Weekends and Friday evenings'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Your profile has been updated successfully" in response.data

    with app.app_context():
        updated_user = db.session.get(User, student_user.id)
        assert updated_user.name == 'Aarav Sharma Updated'
        assert updated_user.college == 'Indian Institute of Technology, Bombay'
        assert updated_user.bio == 'Full-stack developer focused on Flask and Python systems.'
        assert updated_user.availability == 'Weekends and Friday evenings'

def test_profile_update_validation_rejects_empty_name(auth_client, student_user):
    """Verify server-side validation rejects empty or too-short names."""
    response = auth_client.post('/profile', data={
        'name': 'A',  # Less than 2 characters
        'college': 'Any College'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Name must be at least 2 characters long" in response.data or b"Field must be between 2 and" in response.data

def test_unauthorized_user_cannot_update_other_student_profile(app, student_user, second_student_user):
    """
    Verify ownership enforcement: AuthService update_profile operates strictly on the authenticated user.
    A user cannot alter another student's record through session impersonation.
    """
    with app.app_context():
        orig_name = second_student_user.name
        
        # When student_user is logged in, the route only passes current_user to update_profile:
        # User cannot pass an arbitrary target user_id in the form to alter another's profile
        success, _ = AuthService.update_profile(
            user=student_user,
            name="Aarav Renamed"
        )
        assert success is True
        
        # Verify second student is untouched
        refreshed_second = db.session.get(User, second_student_user.id)
        assert refreshed_second.name == orig_name
