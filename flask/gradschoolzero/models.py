from datetime import datetime, date
from gradschoolzero import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=False)


class StudentApplicant(Applicant):
    __tablename__ = 'student_applicant'
    id = db.Column(db.Integer, db.ForeignKey('applicant.id'), primary_key=True)
    gpa = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"StudentApplicant('{self.first_name}', '{self.last_name}', '{self.email}', '{self.dob}', '{self.gpa}')"


class InstructorApplicant(Applicant):
    __tablename__ = 'instructor_applicant'
    id = db.Column(db.Integer, db.ForeignKey('applicant.id'), primary_key=True)
    discipline = db.Column(db.String(20), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    logged_in_before = db.Column(db.Boolean, nullable=False, default=False)
    type = db.Column(db.String(10), nullable=False)
    

class Student(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    gpa = db.Column(db.Float, nullable=False)
    special_registration = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    courses_enrolled = db.relationship('StudentCourseEnrollment', back_populates='students')
    complaints_filed = db.relationship('StudentComplaint', back_populates='students')
    warnings = db.relationship('StudentWarning', backref='student')


    def __repr__(self):
        return f"Student('{self.username}','{self.gpa}')"


class Instructor(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.String, nullable=False)

    sections = db.relationship('CourseSection', back_populates='instructor')
    complaints_filed = db.relationship('InstructorComplaint', back_populates='instructors')
    warnings = db.relationship('InstructorWarning', backref='instructor', lazy=True)


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    course_name = db.Column(db.String(50), nullable=False)
    avg_rating = db.Column(db.Float)


class CourseSection(db.Model):
    __tablename__ = 'course_section'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    section_size = db.Column(db.Integer, nullable = False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    days = db.Column(db.String(27), nullable=False)
    semester = db.Column(db.String(6), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

    instructor = db.relationship('Instructor', back_populates='sections')
    courses = db.relationship('Course', backref='section')
    students_enrolled = db.relationship('StudentCourseEnrollment', back_populates='courses')


class StudentCourseEnrollment(db.Model):
    __tablename__ = 'student_course_enrollment'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    course_section_id = db.Column(db.Integer, db.ForeignKey('course_section.id'), nullable=False)
    grade = db.Column(db.String(1))

    students = db.relationship('Student', back_populates='courses_enrolled')
    courses = db.relationship('CourseSection', back_populates='students_enrolled')

    def __repr__(self):
        return f"StudentCourseEnrollment('{self.id}', '{self.student_id}', '{self.course_section_id}', '{self.grade}')"

    
class CensorWord(db.Model):
    __tablename__ = 'censor_word'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(20), nullable=False)


class CourseReview(db.Model):
    __tablename__ = 'course_review'
    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.Integer,  nullable=False)
    content = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    students = db.relationship('Student', backref='author', lazy=True)
    
    
class StudentComplaint(db.Model):
    __tablename__ = 'student_complaint'
    id = db.Column(db.Integer, primary_key=True)
    date_filed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comlaint = db.Column(db.Text, nullable=False)
    compainee_id = db.Column(db.Integer, nullable=False)
    comlainee_type = db.Column(db.String(10), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    students = db.relationship('Student', back_populates='complaints_filed')


class InstructorComplaint(db.Model):
    __tablename__ = 'instructor_complaint'
    id = db.Column(db.Integer, primary_key=True)
    date_filed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comlaint = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

    instructors = db.relationship('Instructor', back_populates='complaints_filed')


class Warning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_received = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    warning = db.Column(db.Text, nullable=False)


class StudentWarning(Warning):
    __tablename__ = 'student_warning'
    id = db.Column(db.Integer, db.ForeignKey('warning.id'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)


class InstructorWarning(Warning):
    __tablename__ = 'instructor_warning'
    id = db.Column(db.Integer, db.ForeignKey('warning.id'), primary_key=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'), nullable=False)

