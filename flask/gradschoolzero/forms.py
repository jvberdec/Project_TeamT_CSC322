from secrets import choice
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, PasswordField, SubmitField
from wtforms import BooleanField, SelectField, DateField, TimeField, IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError, EqualTo
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms_sqlalchemy.fields import QuerySelectField
from gradschoolzero.models import Applicant, User, Course, Instructor, CourseSection


class ApplicationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=1, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    dob = DateField('Date of Birth (mm-dd-yyyy)', format='%m-%d-%Y', validators=[DataRequired()])
    submit = SubmitField('Apply')


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


class CreateCourseForm(FlaskForm):
    course_code = IntegerField('Course Code', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Create Course')

    def validate_course_code(self, course_code):
        course_code = Course.query.filter_by(id=course_code.data).first()
        if course_code:
            raise ValidationError('Course code already exists. Please double check')


def all_courses():
    return Course.query.order_by(Course.id)

def all_instructors():
    return Instructor.query.order_by(Instructor.first_name)


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class ClassSetUpForm(FlaskForm):
    days_list = [('monday', 'Monday'),
                 ('tuesday', 'Tuesday'),
                 ('wednesday', 'Wednesday'),
                 ('thursday', 'Thursday'),
                 ('friday', 'Friday'),
                 ('saturday', 'Saturday'),
                 ('sunday', 'Sunday')]

    course = QuerySelectField('Course Name', validators=[DataRequired()], query_factory=all_courses)
    instructor_name = QuerySelectField('Instructor Name', validators=[DataRequired()], query_factory=all_instructors)
    class_size = IntegerField('Class Size', validators=[DataRequired()])
    start_time = TimeField('Start Time (Hours:Minutes)', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time (Hours:Minutes)', format='%H:%M', validators=[DataRequired()])
    day = SelectField('Day', choices=days_list)
    submit = SubmitField('Create Section')


class ChangePeriodForm(FlaskForm):
    period = SelectField(u'Change period', choices=[('class_set-up', 'Class Set-up'), 
                                                   ('course_registration', 'Course Registration'), 
                                                   ('class_running', 'Class Running'),
                                                   ('grading', 'Grading')], validators=[DataRequired()])
    submit = SubmitField('Submit')


def all_sections():
    return CourseSection.query


class StudentClassEnrollForm(FlaskForm):
    class_name = QuerySelectField('Course Name', query_factory=all_courses, allow_blank=True)
    instructor_name = QuerySelectField('Instructor Name', query_factory=all_instructors, allow_blank=True)
    #section_name = QuerySelectField('Section', validators=[DataRequired()], query_factory=all_sections)
    submit = SubmitField('Search')


def all_users_except_registrar():
    return User.query.filter(User.type != 'registrar').order_by(User.type, User.first_name)


class WarningForm(FlaskForm):
    warned_user = QuerySelectField('Select user', validators=[DataRequired()], query_factory=all_users_except_registrar)
    warning_text = TextAreaField('Warning Text', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ComplaintForm(FlaskForm):
    complaint_text = TextAreaField('Complaint Text', validators=[DataRequired()])
    submit = SubmitField('Submit')


class StudentComplaintForm(ComplaintForm):
    complainee_username = StringField('Complainee username', validators=[DataRequired(), Length(min=2, max=20)])
    user_type = SelectField(u"User type of person you're complaining about", 
                            choices=[('student', 'Student'), ('instructor', 'Instructor')], 
                            validators=[DataRequired()])


class InstructorComplaintForm(ComplaintForm):
    student_list = [  ('student1', 'Student1'),
                        ('student2', 'Student2'),
                        ('Student3', 'Student3'),
                    ]
    complaint_name = SelectField("Name of person you're complaining about", choices=student_list, validators=[DataRequired(), Length(min=2, max=20)])


class StudentGraduationForm(FlaskForm):
    username = StringField('Your Username', validators=[DataRequired(), Length(min=2, max=20)])
    class_num = IntegerField('Number of classes taken', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change Password')
