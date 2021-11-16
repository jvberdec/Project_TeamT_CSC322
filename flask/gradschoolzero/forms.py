from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, PasswordField, SubmitField
from wtforms import BooleanField, SelectField, DateField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError
from gradschoolzero.models import Applicant, User


class ApplicationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth (mm-dd-yyyy)', format='%m-%d-%Y', validators=[DataRequired()])
    submit = SubmitField('Apply')

    def validate_applicant(self, first_name, last_name, email, dob):
        applicant = Applicant.query.filter_by(first_name=first_name.data, 
                                              last_name=last_name.data, 
                                              email=email.data, 
                                              dob=dob.data).first()

        if applicant:
            raise ValidationError('You have already applied')

        applicant = User.query.filter_by(first_name=first_name.data, 
                                         last_name=last_name.data, 
                                         email=email.data, 
                                         dob=dob.data).first()

        if applicant:
            raise ValidationError('You are already enrolled')


class StudentApplicationForm(ApplicationForm):
    gpa = DecimalField('GPA', validators=[DataRequired(), NumberRange(min=0.0, max=4.0)])
    
class InstructorApplicationForm(ApplicationForm):
    discipline = StringField('Discipline', validators=[DataRequired(), Length(min=1, max=20)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    user_type = SelectField(u'User Type', choices=[('student', 'Student'), 
                                                   ('instructor', 'Instructor'), 
                                                   ('registrar', 'Registrar')], validators=[DataRequired()])
    submit = SubmitField('sign in')

