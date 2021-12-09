from datetime import datetime, date

from sqlalchemy.sql.schema import ForeignKey
from gradschoolzero import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class SchoolInfo(db.Model):
    __tablename__ = 'school_info'
    id = db.Column(db.Integer, primary_key=True)
    current_period = db.Column(db.String(20), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_semester = db.Column(db.String(11), nullable=False)

    def __repr__(self):
        return f'Period({self.current_period}, {self.capacity})'

    def __str__(self):
        return f"{self.current_period.replace('_', ' ').title()}"


class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=False)

    def __repr__(self):
        return f'Applicant({self.first_name}, {self.last_name}, {self.email}, {self.dob})'


class StudentApplicant(Applicant):
    __tablename__ = 'student_applicant'
    id = db.Column(db.Integer, db.ForeignKey('applicant.id'), primary_key=True)
    gpa = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'StudentApplicant({self.first_name}, {self.last_name}, {self.email}, {self.dob}, {self.gpa})'


class InstructorApplicant(Applicant):
    __tablename__ = 'instructor_applicant'
    id = db.Column(db.Integer, db.ForeignKey('applicant.id'), primary_key=True)
    discipline = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'InstructorApplicant({self.first_name}, {self.last_name}, {self.email}, {self.dob}, {self.discipline})'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    empl_id = db.Column(db.Integer)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    logged_in_before = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(20), nullable=False, default='GOOD STANDING')
    suspension_end_semester = db.Column(db.String(11))
    type = db.Column(db.String(10), nullable=False)

    warnings = db.relationship('Warning', back_populates='user')
    complaints_filed_against = db.relationship('Complaint', foreign_keys='Complaint.complainee_id', back_populates='complainee')
    complaints_filed = db.relationship('Complaint', foreign_keys='Complaint.filer_id', back_populates='filer')
    
    def __repr__(self):
        return f'User({self.username}, {self.email}, {self.first_name}, {self.last_name}, {self.logged_in_before}, {self.type})'

    def __str__(self):
        return f'{self.first_name} {self.last_name} | {self.type}'
    

class Student(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    gpa = db.Column(db.Float, nullable=False)
    special_registration = db.Column(db.Boolean, nullable=False, default=False)
    honor_roll_count = db.Column(db.Integer, nullable=False, default=0)

    reviews = db.relationship('CourseReview', back_populates='author')
    courses_enrolled = db.relationship('StudentCourseEnrollment', back_populates='student', lazy='dynamic')
    courses_waitlisted = db.relationship('Waitlist', back_populates='student', lazy='dynamic')

    def __repr__(self):
        return f'Student({self.username}, {self.email}, {self.first_name}, {self.last_name}, {self.logged_in_before}, {self.type}, {self.gpa}, {self.special_registration}, {self.status})'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Instructor(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    discipline = db.Column(db.String(20), nullable=False)

    courses = db.relationship('Course', back_populates='instructor', lazy='dynamic')

    def __repr__(self):
        return f'Instructor({self.username}, {self.email}, {self.first_name}, {self.last_name}, {self.logged_in_before}, {self.type}, {self.discipline}, {self.status})'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    major = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'Major({self.major})'


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    course_name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=0)
    number_enrolled = db.Column(db.Integer, nullable=False, default=0)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    day = db.Column(db.String(9), nullable=False)
    is_full = db.Column(db.Boolean, nullable=False, default=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)
    avg_rating = db.Column(db.Float)
    avg_gpa = db.Column(db.Float)
    status = db.Column(db.String(8), nullable=False, default='NOT SET')
    
    instructor = db.relationship('Instructor', back_populates='courses')
    students_enrolled = db.relationship('StudentCourseEnrollment', back_populates='course', lazy='dynamic')
    students_waitlisted = db.relationship('Waitlist', back_populates='course')
    reviews = db.relationship('CourseReview', back_populates='course')

    def __repr__(self):
        return f'Course({self.id}, {self.course_name}, {self.capacity}, {self.start_time}, {self.end_time}, {self.day}, {self.avg_rating})'

    def __str__(self):
        return f'{self.id} {self.course_name}'.title()


class StudentCourseEnrollment(db.Model):
    __tablename__ = 'student_course_enrollment'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    grade = db.Column(db.String(1))
    semester = db.Column(db.String(11), nullable=False)

    student = db.relationship('Student', back_populates='courses_enrolled')
    course = db.relationship('Course', back_populates='students_enrolled')

    def __repr__(self):
        return f'StudentCourseEnrollment({self.student_id}, {self.course_id}, {self.grade}, {self.semester})'


class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    student = db.relationship('Student', back_populates='courses_waitlisted')
    course = db.relationship('Course', back_populates='students_waitlisted')

    def __repr__(self):
        return f'Waitlist({self.student_id}, {self.course_section_id})'

    
class CensorWord(db.Model):
    __tablename__ = 'censor_word'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'CensorWord({self.word})'


class CourseReview(db.Model):
    __tablename__ = 'course_review'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    taboo_word_count = db.Column(db.Integer, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    course = db.relationship('Course', back_populates='reviews')
    author = db.relationship('Student', back_populates='reviews')

    def __repr__(self):
        return f'CourseReview({self.course_code}, {self.student_id})'


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint = db.Column(db.Text, nullable=False)
    date_filed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    complainee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    complainee = db.relationship('User', foreign_keys='Complaint.complainee_id', back_populates='complaints_filed_against')
    filer = db.relationship('User', foreign_keys='Complaint.filer_id', back_populates='complaints_filed')


class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_received = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    warning = db.Column(db.Text, nullable=False)    

    user = db.relationship('User', back_populates='warnings')

    def __repr__(self):
        return f'Warning({self.date_received}, {self.user_id})'
