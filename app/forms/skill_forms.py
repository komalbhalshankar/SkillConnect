"""
WTForms definitions for Skill portfolio management, Discovery filters, and Admin skill curation.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class AddUserSkillForm(FlaskForm):
    category_id = SelectField('Skill Category', coerce=int, validators=[Optional()])
    skill_id = SelectField('Select Skill', coerce=int, validators=[
        DataRequired(message="Please select a skill.")
    ])
    custom_skill_name = StringField('Or Enter New Skill Name', validators=[
        Optional(),
        Length(min=2, max=100, message="Skill name must be between 2 and 100 characters.")
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
    skill_type = SelectField('Skill Intent', choices=[
        ('teach', 'Teach (I can offer this skill)'),
        ('learn', 'Learn (I wish to learn this skill)')
    ], validators=[DataRequired()])
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

class DiscoveryFilterForm(FlaskForm):
    q = StringField('Search by Skill Name', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[Optional()])
    proficiency = SelectField('Proficiency', choices=[
        ('', 'All Proficiency Levels'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ], default='', validators=[Optional()])
    intent = SelectField('Looking For Students Who', choices=[
        ('all', 'Either Teach or Learn'),
        ('teach', 'Can Teach (Mentors)'),
        ('learn', 'Want to Learn (Peers)')
    ], default='all', validators=[Optional()])
    submit = SubmitField('Filter')

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
