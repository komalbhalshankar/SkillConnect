"""
WTForms definitions for Skill portfolio management and Admin skill curation.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional

class AddUserSkillForm(FlaskForm):
    skill_id = SelectField('Select Skill', coerce=int, validators=[
        DataRequired(message="Please select a skill.")
    ])
    skill_type = SelectField('Skill Intent', choices=[
        ('teach', 'I want to Teach this skill'),
        ('learn', 'I want to Learn this skill')
    ], validators=[DataRequired()])
    proficiency = SelectField('Proficiency Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='intermediate', validators=[DataRequired()])
    notes = StringField('Notes (Optional e.g., topics, experience level)', validators=[
        Optional(),
        Length(max=200, message="Notes must be 200 characters or fewer.")
    ])
    submit = SubmitField('Add Skill to Portfolio')

class EditUserSkillForm(FlaskForm):
    proficiency = SelectField('Proficiency Level', choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], validators=[DataRequired()])
    notes = StringField('Notes (Optional)', validators=[
        Optional(),
        Length(max=200)
    ])
    submit = SubmitField('Update Skill')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[
        DataRequired(message="Category name is required."),
        Length(min=2, max=80)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=255)
    ])
    icon = StringField('Bootstrap Icon Class (e.g. bi-code-slash)', default='bi-tag', validators=[
        DataRequired()
    ])
    submit = SubmitField('Save Category')

class AdminSkillForm(FlaskForm):
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    name = StringField('Skill Name', validators=[
        DataRequired(message="Skill name is required."),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Skill Description', validators=[
        Optional(),
        Length(max=255)
    ])
    submit = SubmitField('Create Skill')
