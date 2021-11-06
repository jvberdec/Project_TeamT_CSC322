from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, NumberRange


class ApplicationForm(FlaskForm):
    first_name = StringField('first name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('last name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('apply')


class StudentAppplicationForm(ApplicationForm):
    gpa = DecimalField('gpa', validators=[DataRequired(), NumberRange(min=0.0, max=4.0)])


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('password', validators=[DataRequired])
    remember = BooleanField('remember me')
    submit = SubmitField('login')

