"""
WTForms definitions for Rating and Feedback.
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class RatingForm(FlaskForm):
    score = SelectField('Your Rating', coerce=int, choices=[
        (5, '★★★★★ (5 Stars - Outstanding Experience)'),
        (4, '★★★★☆ (4 Stars - Very Good & Helpful)'),
        (3, '★★★☆☆ (3 Stars - Good & Satisfactory)'),
        (2, '★★☆☆☆ (2 Stars - Needs Improvement)'),
        (1, '★☆☆☆☆ (1 Star - Poor / Did Not Deliver)')
    ], default=5, validators=[DataRequired(message="Please select a rating score.")])
    feedback = TextAreaField('Constructive Feedback & Comments', validators=[
        Optional(),
        Length(max=500, message="Feedback must be 500 characters or fewer.")
    ])
    submit = SubmitField('Submit Rating & Review')
