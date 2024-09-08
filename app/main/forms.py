from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Email, DataRequired
# from app.models import User
# from flask import current_app


class AddUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name')
    last_name = StringField('Last name')
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True, 'class': 'cancel btn-secondary'})


class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', render_kw={'readonly': True})
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name')


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name')
    last_name = StringField('Last name')


class RoleForm(FlaskForm):
    name = StringField('Role name', validators=[DataRequired()])
    description = StringField('Description')

    