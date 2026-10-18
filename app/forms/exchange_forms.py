"""
WTForms definitions for Exchange Requests and Session Scheduling.
"""
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, TextAreaField, StringField, IntegerField, DateField, TimeField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class CreateExchangeRequestForm(FlaskForm):
    receiver_id = HiddenField('Receiver ID', validators=[DataRequired()])
    offered_skill_id = SelectField('Skill You Will Teach', coerce=int, validators=[
        DataRequired(message="Please select the skill you will teach.")
    ])
    requested_skill_id = SelectField('Skill You Want to Learn', coerce=int, validators=[
        DataRequired(message="Please select the skill you want to learn.")
    ])
    message = TextAreaField('Introductory Note & Expectations', validators=[
        Optional(),
        Length(max=500, message="Message must be 500 characters or fewer.")
    ])
    submit = SubmitField('Send Exchange Request')

class ScheduleSessionForm(FlaskForm):
    request_id = HiddenField('Request ID', validators=[DataRequired()])
    scheduled_date = DateField('Session Date', validators=[DataRequired(message="Date is required.")])
    scheduled_time = TimeField('Session Time', validators=[DataRequired(message="Time is required.")])
    duration_minutes = IntegerField('Duration (Minutes)', default=60, validators=[
        DataRequired(),
        NumberRange(min=15, max=300, message="Duration must be between 15 and 300 minutes.")
    ])
    mode = SelectField('Learning Mode', choices=[
        ('online', 'Online (Google Meet / Zoom / Discord)'),
        ('in_person', 'In-Person (Campus Library / Lab)'),
        ('hybrid', 'Hybrid')
    ], default='online', validators=[DataRequired()])
    meeting_details = StringField('Meeting Link or Physical Location', validators=[
        Optional(),
        Length(max=255, message="Details too long.")
    ])
    notes = TextAreaField('Agenda / Topics to Cover', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Confirm & Schedule Session')
