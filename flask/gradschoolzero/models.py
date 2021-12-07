from datetime import datetime, date
from gradschoolzero import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class SemesterPeriod(db.Model):
    __tablename__ = 'semester_period'
    id = db.Column(db.Integer, primary_key=True)
    current_period = db.Column(db.String(20), nullable=False, default='class set-up')
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)

    current_semester = db.relationship('Semester', back_populates='semester_period')

    def __repr__(self):
        return f'Period({self.current_period}, {self.semester_id})'

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
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    logged_in_before = db.Column(db.Boolean, nullable=False, default=False)
    type = db.Column(db.String(10), nullable=False)
    
    def __repr__(self):
        return f'User({self.username}, {self.email}, {self.first_name}, {self.last_name}, {self.logged_in_before}, {self.type})'
    

class Student(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    gpa = db.Column(db.Float, nullable=False)
    special_registration = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.String(20), nullable=False, default='GOOD STANDING')

    courses_enrolled = db.relationship('StudentCourseEnrollment', back_populates='student', lazy='dynamic')
    courses_waitlisted = db.relationship('Waitlist', back_populates='students', lazy='dynamic')
    complaints_filed = db.relationship('StudentComplaint', back_populates='students')
    warnings = db.relationship('StudentWarning', backref='student')

    def __repr__(self):
        return f'Student({self.username}, {self.email}, {self.first_name}, {self.last_name}, {self.logged_in_before}, {self.type}, {self.gpa}, {self.special_registration}, {self.status})'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Instructor(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    discipline = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String, nullable=False, default='GOOD STANDING')

    sections = db.relationship('CourseSection', back_populates='instructor')
    complaints_filed = db.relationship('InstructorComplaint', back_populates='instructors')
    warnings = db.relationship('InstructorWarning', backref='instructor')

    def __repr__(self):
        return f'Instructor({self.username}, {self.email}, {self.first_name}, {self.last_name}, {self.logged_in_before}, {self.type}, {self.discipline}, {self.status})'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    major = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'Major({self.major})'


class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semester_name = db.Column(db.String(8), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    sections = db.relationship('CourseSection', back_populates='semester')
    semester_period = db.relationship('SemesterPeriod', back_populates='current_semester')

    def __repr__(self):
        return f'Semester({self.semester_name}, {self.year})'

    def __str__(self):
        return f'{self.semester_name} {self.year}'.title()


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    course_name = db.Column(db.String(50), nullable=False)
    avg_rating = db.Column(db.Float)

    def __repr__(self):
        return f'Course({self.course_name}, {self.avg_rating})'

    def __str__(self):
        return f'{self.id} {self.course_name}'.title()


class CourseSection(db.Model):
    __tablename__ = 'course_section'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    section_size = db.Column(db.Integer, nullable = False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    day = db.Column(db.String(9), nullable=False)
    is_full = db.Column(db.Boolean, nullable=False, default=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semester.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

    course = db.relationship('Course', backref='section')
    semester = db.relationship('Semester', back_populates='sections')
    instructor = db.relationship('Instructor', back_populates='sections')
    students_enrolled = db.relationship('StudentCourseEnrollment', back_populates='section')
    students_waitlisted = db.relationship('Waitlist', back_populates='courses')

    def __repr__(self):
        return f'CourseSection({self.course_code}, {self.section_size}, {self.start_time}, {self.end_time}, {self.day})'


class StudentCourseEnrollment(db.Model):
    __tablename__ = 'student_course_enrollment'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_section_id = db.Column(db.Integer, db.ForeignKey('course_section.id'), nullable=False)
    grade = db.Column(db.String(1))

    student = db.relationship('Student', back_populates='courses_enrolled')
    section = db.relationship('CourseSection', back_populates='students_enrolled')

    def __repr__(self):
        return f'StudentCourseEnrollment({self.student_id}, {self.course_section_id}, {self.grade})'



class Waitlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_section_id = db.Column(db.Integer, db.ForeignKey('course_section.id'), nullable=False)

    students = db.relationship('Student', back_populates='courses_waitlisted')
    courses = db.relationship('CourseSection', back_populates='students_waitlisted')

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
    course_code = db.Column(db.Integer,  nullable=False)
    content = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    students = db.relationship('Student', backref='author', lazy=True)

    def __repr__(self):
        return f'CourseReview({self.course_code}, {self.student_id})'

    
    
class StudentComplaint(db.Model):
    __tablename__ = 'student_complaint'
    id = db.Column(db.Integer, primary_key=True)
    date_filed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comlaint = db.Column(db.Text, nullable=False)
    compainee_id = db.Column(db.Integer, nullable=False)
    comlainee_type = db.Column(db.String(10), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    students = db.relationship('Student', back_populates='complaints_filed')

    def __repr__(self):
        return f'StudentComplaint({self.date_filed}, {self.compainee_id}, {self.comlainee_type}, {self.student_id})'


class InstructorComplaint(db.Model):
    __tablename__ = 'instructor_complaint'
    id = db.Column(db.Integer, primary_key=True)
    date_filed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comlaint = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

    instructors = db.relationship('Instructor', back_populates='complaints_filed')

    def __repr__(self):
        return f'InstructorComplaint({self.date_filed}, {self.student_id}, {self.instructor_id})'


class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_received = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    warning = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'Warning({self.date_received})'


class StudentWarning(Warning):
    __tablename__ = 'student_warning'
    id = db.Column(db.Integer, db.ForeignKey('warning.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    def __repr__(self):
        return f'StudentWarning({self.date_received}, {self.student_id})'


class InstructorWarning(Warning):
    __tablename__ = 'instructor_warning'
    id = db.Column(db.Integer, db.ForeignKey('warning.id'), primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

    def __repr__(self):
        return f'InstructorWarning({self.date_received}, {self.instructor_id})'

