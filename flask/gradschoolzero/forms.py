from secrets import choice
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, PasswordField, SubmitField
from wtforms import BooleanField, SelectField, DateField, TimeField, IntegerField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, NumberRange, ValidationError, EqualTo
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms_sqlalchemy.fields import QuerySelectField
from gradschoolzero.models import Applicant, User, Course, Semester, Instructor, CourseSection


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


class CreateCourseForm(FlaskForm):
    course_code = IntegerField('Course Code', validators=[DataRequired()])
    course_name = StringField('Course Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Submit Course')

    def validate_course_code(self, course_code):
        course_code = Course.query.filter_by(id=course_code.data).first()
        if course_code:
            raise ValidationError('Course code already exists. Please double check')


class CreateSemesterForm(FlaskForm):
    semester_name = SelectField(u'Semester', choices=[('fall', 'Fall'), ('spring', 'Spring')], validators=[DataRequired()])
    start_date = DateField('Start Date (mm-dd-yyyy)', format='%m-%d-%Y', validators=[DataRequired()])
    end_date = DateField('End Date (mm-dd-yyyy)', format='%m-%d-%Y', validators=[DataRequired()])
    submit = SubmitField('Submit Semester')

    def validate_semester(self, semester_name, start_date):
        course_code = Semester.query.filter_by(semester_name=semester_name.data, year=start_date.year).first()
        if course_code:
            raise ValidationError('Semester already exists. Please double check')


def all_courses():
    return Course.query.order_by(Course.id)

def all_semesters():
    return Semester.query.order_by(Semester.year)

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
    semester = QuerySelectField('Semester', validators=[DataRequired()], query_factory=all_semesters)
    start_time = TimeField('Start Time (Hours:Minutes)', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('Start Time (Hours:Minutes)', format='%H:%M', validators=[DataRequired()])
    day = SelectField('Day', choices=days_list)
    submit = SubmitField('Submit Section')


class ChangePeriodForm(FlaskForm):
    period = SelectField(u'Change period', choices=[('class_set-up', 'Class Set-up'), 
                                                   ('course_registration', 'Course Registration'), 
                                                   ('class_running', 'Class Running'),
                                                   ('grading', 'Grading')], validators=[DataRequired()])
    submit = SubmitField('Submit')


def all_sections():
    return CourseSection.query


class StudentClassEnrollForm(FlaskForm):
    #these lists will have to be populated from the database
    class_list = [  ('science', 'Science'),
                    ('math', 'Math'),
                    ('cs_science', 'Computer Science'),
                    ('English', 'English'),
                    ('philosophy', 'Philosophy'),
                ]

    instructor_list = [  ('bob_builder', 'Bob Builder'),
                        ('bobby_brown', 'Bobby Brown'),
                        ('bobby_bobby', 'Bobby Bobby'),
                        ('bob_bob', 'Bob Bob'),
                        ('builder_bob', 'Builder Bob'),
                    ]

    section_list = [    ('section_a', 'Section A (11-12pm)'),
                        ('section_b', 'Section B (2-3:40pm)'),
                        ('section_c', 'Section C (5-6:30pm)'),
                    ]
    class_name = QuerySelectField('Course Name', validators=[DataRequired()], query_factory=all_courses)
    instructor_name = QuerySelectField('Instructor Name', validators=[DataRequired()], query_factory=all_instructors)
    section_name = QuerySelectField('Section', validators=[DataRequired()], query_factory=all_sections)
    submit = SubmitField('Submit')



class WarningForm(FlaskForm):

    instructor_list = [  ('bob_builder', 'Bob Builder'),
                        ('bobby_bobby', 'Bobby Bobby'),
                        ('bob_bob', 'Bob Bob'),
                        ('builder_bob', 'Builder Bob'),
                    ]

    student_list = [  ('student1', 'Student1'),
                        ('student2', 'Student2'),
                        ('Student3', 'Student3'),      
                    ]

    instructor_list.extend(student_list)
    all_users = instructor_list[:]

    username = StringField('Your Username', validators=[DataRequired(), Length(min=2, max=20)])
    warned_name = SelectField('Name of Warned Person', choices=all_users, validators=[DataRequired(), Length(min=2, max=20)])
    user_type = SelectField(u'User Type of Warned Person', choices=[('student', 'Student'), ('instructor', 'Instructor')], 
                                                            validators=[DataRequired()])
    warning_text = TextAreaField('Warning Text', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ComplaintForm(FlaskForm):
    username = StringField('Your Username', validators=[DataRequired(), Length(min=2, max=20)])
    complaint_text = TextAreaField('Complaint Text', validators=[DataRequired()])
    submit = SubmitField('Submit')


class StudentComplaintForm(ComplaintForm):
    instructor_list = [  ('bob_builder', 'Bob Builder'),
                        ('bobby_bobby', 'Bobby Bobby'),
                        ('bob_bob', 'Bob Bob'),
                        ('builder_bob', 'Builder Bob'),
                    ]

    student_list = [  ('student1', 'Student1'),
                        ('student2', 'Student2'),
                        ('Student3', 'Student3'),      
                    ]

    instructor_list.extend(student_list)
    all_users = instructor_list[:]

    complaint_name = SelectField("Name of person you're complaining about", choices=all_users, validators=[DataRequired(), Length(min=2, max=20)])
    user_type = SelectField(u"User type of person you're complaining about", choices=[('student', 'Student'), ('instructor', 'Instructor')], 
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
