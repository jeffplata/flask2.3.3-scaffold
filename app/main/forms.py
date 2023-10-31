from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email
from app.models import User


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
    # submit = SubmitField('Submit')
    # cancel = SubmitField('Cancel', render_kw={'formnovalidate': True, 'class': 'btn-secondary'})


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name')
    last_name = StringField('Last name')

    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different username.')
    #
    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')
