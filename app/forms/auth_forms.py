"""
WTForms definitions for user authentication and profile management.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[
        DataRequired(message="Email is required."),
        Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required.")
    ])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(message="Full name is required."),
        Length(min=2, max=100, message="Name must be between 2 and 100 characters.")
    ])
    email = StringField('College / Personal Email', validators=[
        DataRequired(message="Email is required."),
        Email(message="Please enter a valid email address.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=6, max=128, message="Password must be at least 6 characters.")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message="Passwords must match.")
    ])
    college = StringField('College / University', validators=[
        Optional(),
        Length(max=150, message="College name too long.")
    ])
    bio = TextAreaField('About You / Academic Interests', validators=[
        Optional(),
        Length(max=500, message="Bio must be 500 characters or fewer.")
    ])
    availability = StringField('Weekly Availability (e.g., Evenings & Weekends)', validators=[
        Optional(),
        Length(max=100, message="Availability description too long.")
    ])
    submit = SubmitField('Create Account')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(message="Full name is required."),
        Length(min=2, max=100)
    ])
    college = StringField('College / University', validators=[
        Optional(),
        Length(max=150)
    ])
    bio = TextAreaField('Bio / Learning Goals', validators=[
        Optional(),
        Length(max=500)
    ])
    availability = StringField('Weekly Availability', validators=[
        Optional(),
        Length(max=100)
    ])
    submit = SubmitField('Save Profile Changes')
