from secrets import choice
from string import ascii_letters, digits, punctuation
import re
from flask import redirect, url_for, render_template, flash, request
from wtforms import validators 
#from werkzeug.wrappers import response
from gradschoolzero import app, db, bcrypt, mail
from gradschoolzero.forms import *
from gradschoolzero.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
from sqlalchemy import or_


def generate_username(first_name, last_name):
    first_initial = first_name[0]
    last_six = last_name[:6]

    partial_username = (first_initial + last_six).lower()

    existing_students = Student.query.filter(Student.username.startswith(partial_username)).all()

    if existing_students:
        last_student_username = existing_students[-1].username
        username = re.sub(r'[0-9]+$',
                          lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",
                          last_student_username)

    else:
        username = partial_username + '000'

    return username


def generate_password():
    characters = ascii_letters + digits + punctuation
    password = ''.join(choice(characters) for i in range(16))

    return password


def generate_email_content(response_dict):
    content = ''
    if response_dict['application'] == 'accepted':
        content = (f'Congratulations on being accepted to GradSchoolZero! Below is your login information to access your {response_dict["type"]} dashboard:\n\n'
                   f'Username: {response_dict["username"]}\n'
                   f'Password: {response_dict["password"]}')

    elif response_dict['application'] == 'rejected':
        content = f'Unfortunately you have not been accepted to GradSchoolZero.\n\n'
        
        if 'reason' in response_dict:
            content = content + (f'Reason:\n'
                                 f'{response_dict["reason"]}')

    return content


def send_email(recipient, body):
    msg = Message('GradSchoolZero Admissions', recipients=[recipient])
    msg.body = body
    mail.send(msg)


@app.route("/")
@app.route("/home")
def home():
    # return "Home Page"
    return render_template("index.html")


@app.route("/login/", methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data.strip(), type=login_form.user_type.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            if current_user.type == 'student':
                if current_user.logged_in_before:
                    return redirect(url_for('student_dash'))
                else:
                    return redirect(url_for('change_password'))
            elif current_user.type == 'instructor':
                if current_user.logged_in_before:
                    return redirect(url_for('instructor_dash'))
                else:
                    return redirect(url_for('change_password'))
            elif current_user.type == 'registrar':
                return redirect(url_for('registrar_default_dash'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=login_form)


@app.route("/change_password", methods=['POST', 'GET'])
@login_required
def change_password():
    change_password_form = ChangePasswordForm()
    if change_password_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(change_password_form.password.data).decode('utf-8')
        current_user.password = hashed_password
        current_user.logged_in_before = True
        db.session.commit()
        flash('Your password has been updated!', 'success')
        if current_user.type == 'student':
            return redirect(url_for('student_dash'))
        if current_user.type == 'instructor':
            return redirect(url_for('instructor_dash'))
    return render_template('change_password.html', title='Change Password', form=change_password_form)


@app.route("/student_app", methods=['POST', 'GET'])
def student_app():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    student_app_form = StudentApplicationForm()
    if student_app_form.validate_on_submit():
        applicant_applied = StudentApplicant.query.filter_by(first_name=student_app_form.first_name.data.strip(), 
                                                    last_name=student_app_form.last_name.data.strip(),
                                                    email=student_app_form.email.data.strip(), 
                                                    dob=student_app_form.dob.data).first()
        
        applicant_enrolled = User.query.filter_by(first_name=student_app_form.first_name.data.strip(), 
                                                last_name=student_app_form.last_name.data.strip(),
                                                email=student_app_form.email.data.strip()).first()

        if (applicant_applied is None) and (applicant_enrolled is None):
            student_applicant = StudentApplicant(first_name=student_app_form.first_name.data.strip(), 
                                                    last_name=student_app_form.last_name.data.strip(),
                                                    email=student_app_form.email.data.strip(), 
                                                    dob=student_app_form.dob.data,
                                                    gpa=student_app_form.gpa.data)
            db.session.add(student_applicant)
            db.session.commit()
            flash('Application filed successfully! You will be notified via email of our decision.', 'success')

            return redirect(url_for('login'))
        elif applicant_applied:
            flash("You've already applied!", 'danger')
            return redirect(url_for('home'))
        elif applicant_enrolled:
            flash("You are already enrolled!", 'danger')
            return redirect(url_for('home'))

    return render_template('student_app.html', title='Student Application', form=student_app_form)


@app.route("/instructor_app", methods=['POST', 'GET'])
def instructor_app():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
   
    instructor_app_form = InstructorApplicationForm()
    if instructor_app_form.validate_on_submit():
        applicant_applied = InstructorApplicant.query.filter_by(first_name=instructor_app_form.first_name.data.strip(), 
                                                                last_name=instructor_app_form.last_name.data.strip(),
                                                                email=instructor_app_form.email.data.strip(), 
                                                                dob=instructor_app_form.dob.data).first()
        applicant_enrolled = User.query.filter_by(first_name=instructor_app_form.first_name.data.strip(), 
                                                last_name=instructor_app_form.last_name.data.strip(),
                                                email=instructor_app_form.email.data.strip()).first()

        if (applicant_applied is None) and (applicant_enrolled is None):
            instructor_applicant = InstructorApplicant(first_name=instructor_app_form.first_name.data.strip(), 
                                                    last_name=instructor_app_form.last_name.data.strip(),
                                                    email=instructor_app_form.email.data.strip(), 
                                                    dob=instructor_app_form.dob.data,
                                                    discipline=instructor_app_form.discipline.data.strip())
            db.session.add(instructor_applicant)
            db.session.commit()
            flash('Application filed successfully! You will be notified via email of our decision.', 'success')
            return redirect(url_for('login'))
        elif applicant_applied:
            flash("You've already applied!", 'danger')
            return redirect(url_for('home'))
        elif applicant_enrolled:
            flash("You are already enrolled!", 'danger')
            return redirect(url_for('home'))

    return render_template('instructor_app.html', title='Instructor Application', form=instructor_app_form)

@app.route("/statistics_page")
def statistics_page():
    highest_rated = Course.query.filter(Course.avg_rating != None).order_by(Course.avg_rating.desc()).limit(5).all()
    lowest_rated = Course.query.filter(Course.avg_rating != None).order_by(Course.avg_rating).limit(5).all()
    top_students = Student.query.order_by(Student.gpa.desc()).limit(5).all()
    reviews = CourseReview.query.filter(CourseReview.taboo_word_count <= 2).all()
    return render_template("statistics_page.html", 
                           highest_rated=highest_rated, 
                           lowest_rated=lowest_rated, 
                           top_students=top_students, 
                           reviews=reviews)


@app.route("/student_dash", methods=['POST', 'GET'])
@login_required
def student_dash():
    if current_user.is_authenticated and current_user.type == "student":
        school_info = SchoolInfo.query.first()
        student = Student.query.filter_by(id=current_user.id).first()
        courses_taken = student.courses_enrolled.filter(StudentCourseEnrollment.grade != None).all()
        current_courses = student.courses_enrolled.filter(StudentCourseEnrollment.grade == None).all()
        warnings = student.warnings

        return render_template('student_dash.html', 
                               title='Student Dashboard', 
                               courses_taken=courses_taken, 
                               current_courses=current_courses,
                               warnings=warnings,
                               school_info=school_info,
                               student=student)
    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))


@app.route("/student_dash/dismiss_warning/<int:index>", methods=['POST', 'GET'])
@login_required
def dismiss_warning(index):
    student = Student.query.filter_by(id=current_user.id).first()
    if student.honor_roll_count >= 1:
        student.honor_roll_count -= 1
        warning = Warning.query.filter_by(id=index).first()
        db.session.delete(warning)
        db.session.commit()
        flash('Warning successfully dismissed', 'success')
    else:
        flash('No honor roll placements to use to dismiss warning', 'warning')
    return redirect(url_for('student_dash'))


@app.route("/student_dash/drop_section/<int:index>", methods=['POST', 'GET'])
@login_required
def drop_section(index):
    current_period = SchoolInfo.query.first().current_period
    course_enrolled = StudentCourseEnrollment.query.filter_by(id=index).first()

    if current_period == 'course registration':
        db.session.delete(course_enrolled)
        db.session.commit()
    elif current_period == 'course running':
        course_enrolled.grade = 'W'
        db.session.commit()

    return redirect(url_for('student_dash'))


def replace(match):
    word = match.group()
    censor_words = CensorWord.query.all()
    censor_words = [censor.word for censor in censor_words]
    if word.lower() in censor_words:
        return '*' * len(word)
    else:
        return word


@app.route("/review_course/<int:index>", methods=['POST', 'GET'])
@login_required
def review_course(index):
    print(current_user.id)
    course_review_form = CourseReviewForm()
    if course_review_form.validate_on_submit():
        review_exists = CourseReview.query.filter_by(course_code=index, student_id=current_user.id).first()
        if review_exists:
            flash('Already reviewed this course. Cannot submit another review', 'warning')
        else:
            review_text = course_review_form.review_text.data.strip()
            word_list = [word.strip(punctuation) for word in review_text.lower().split()]
            censor_words = CensorWord.query.all()
            censor_words = [censor.word for censor in censor_words]
            taboo_words_count = sum(any(censor_word == word for censor_word in censor_words) for word in word_list)
            review_text = re.sub(r'\b\w*\b', replace, review_text, flags=re.I|re.U)

            course = ''
            if taboo_words_count >= 1:
                course = Course.query.filter_by(id=index).first()
                warning_message = f'First warning for {course} review due to at least 1 to 2 taboo words detected.'
                issue_warning(current_user.id, warning_message)
            if taboo_words_count >= 3:
                warning_message = f'Second warning for {course} review due to at least 3 taboo words detected. Review will not be posted to school website.'
                issue_warning(current_user.id, warning_message)
                print(warning_message)

            course_review = CourseReview(course_code=index, 
                                         content=review_text, 
                                         rating=course_review_form.star_rating.data,
                                         taboo_word_count=taboo_words_count, 
                                         student_id=current_user.id)
            db.session.add(course_review)
            db.session.commit()
            flash('Review successfully submitted', 'success')

    return render_template('review_course.html', title='Review Course', form=course_review_form)


@app.route("/instructor_dash", methods=['POST', 'GET'])
@login_required
def instructor_dash():
    if current_user.is_authenticated and current_user.type == "instructor":
        school_info = SchoolInfo.query.first()
        instructor = Instructor.query.filter_by(id=current_user.id).first()
        warnings = instructor.warnings

        return render_template('instructor_dash.html', 
                               title='Instructor Dashboard', 
                               instructor_courses=instructor.courses.all(), 
                               school_info=school_info,
                               warnings=warnings)

    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))


@app.route("/instructor_dash/submit_grade/<int:index>", methods=['POST', 'GET'])
@login_required
def submit_grade(index):
    if request.method == 'POST':
        grade = request.form['grade']
        grade = grade.upper()
        if grade not in ['A', 'B', 'C', 'D', 'F']:
            flash("Invalid grade. Letter grade must be one of the following: 'A', 'B', 'C', 'D', or 'F'.", 'warning')
        else:
            student_course_enrolled = StudentCourseEnrollment.query.filter_by(id=index).first()
            student_course_enrolled.grade = grade
            db.session.commit()
            flash('Grade successfully submitted', 'success')

    return redirect(url_for('instructor_dash'))


@app.route("/instructor_dash/accept_from_waitlist/<int:index>", methods=['POST', 'GET'])
@login_required
def accept_from_waitlist(index):
    waitlisted_student = Waitlist.query.filter_by(id=index)
    student_course_enrollment = StudentCourseEnrollment(student_id=waitlisted_student.student_id, course_section_id=waitlisted_student.course_section_id)

    db.session.add(student_course_enrollment)
    db.session.delete(waitlisted_student)
    db.session.commit()

    return redirect(url_for('instructor_dash'))


@app.route("/registrar_default_dash", methods=['POST', 'GET'])
@login_required
def registrar_default_dash(): 
    if current_user.is_authenticated and current_user.type == "registrar":
        students = Student.query.filter(Student.status != 'DISMISSED', Student.status != 'GRADUATED').all()
        instructors = Instructor.query.all()
        change_period_form = ChangePeriodForm()
        school_info = SchoolInfo.query.first()
        if change_period_form.validate_on_submit():
            school_info.current_period = change_period_form.period.data
            db.session.commit()
            flash('Period changed successfully!', 'success')
        print(school_info.current_period)
        return render_template('registrar_dash.html', 
                               title='Registrar Dashboard', 
                               current_period=school_info.current_period, 
                               students=students,
                               instructors=instructors)
    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))


@app.route("/registrar_default_dash/change_capacity/", methods=['POST', 'GET'])
@login_required
def change_capacity():
    if request.method == 'POST':
        capacity = request.form['capacity']
        capacity = int(capacity)
        print(capacity)
        if capacity >= 1:
            school_info = SchoolInfo.query.first()
            school_info.capacity = capacity
            db.session.commit()
        else:
            flash('Value must be >= 1', 'warning')
    return redirect(url_for('registrar_default_dash'))


@app.route("/registrar_default_dash/add_censor_word/", methods=['POST', 'GET'])
@login_required
def add_censor_word():
    if request.method == 'POST':
        censor_word = request.form['censorWord']
        censor_word = censor_word.strip().lower()
        taboo_word = CensorWord(word=censor_word)
        db.session.add(taboo_word)
        db.session.commit()
        print(censor_word)
    return redirect(url_for('registrar_default_dash'))


def calculate_gpa(student_course_enrollment_grade):
    points = 0
    grade_dict = {'A': 4,
                  'B': 3,
                  'C': 2,
                  'D': 1,
                  'F': 0}

    grades = [enrollment.grade for enrollment in student_course_enrollment_grade]
    if grades:
        for grade in grades:
            points += grade_dict[grade]

        gpa = points / len(grades)
        gpa = round(gpa, 2)
    
    return gpa


@app.route("/registrar_default_dash/next_period", methods=['POST', 'GET'])
@login_required
def next_period():
    school_info = SchoolInfo.query.first()

    if school_info.current_period == 'class set-up':
        school_info.current_period = 'course registration'

    elif school_info.current_period == 'course registration':
        school_info.current_period = 'class running'
        courses = Course.query.filter(Course.status != 'NOT SET').all()
        for course in courses:
            # Checks if course enrollment is < 5.
            # if it is, then the course is canceled
            course_enrollment_count = course.number_enrolled
            if course_enrollment_count < 5:
                course.status = 'CANCELED'
                 
        students = Student.query.filter_by(status='GOOD STANDING').all()
        for student in students:
            # checks if the student is enrolled in < 2 courses.
            # if they are, then they are issued a warning. 
            courses_enrolled_count = student.courses_enrolled.filter_by(semester=school_info.current_semester).count()
            if courses_enrolled_count < 2:
                issue_warning(student.id, 'Currently enrolled in < 2 courses')
            # checks if any of the student's courses have been canceled.
            # if is has, then they are given the special registration period.
            canceled_course = student.courses_enrolled.filter(StudentCourseEnrollment.course.has(status='CANCELED')).first()
            if canceled_course:
                student.special_registration = True

        # Unenrolls student from canceled course
        canceled_enrollment = StudentCourseEnrollment.query.filter(StudentCourseEnrollment.course.has(status='CANCELED')).all()
        for canceled in canceled_enrollment:
            db.session.delete(canceled)
        instructors = Instructor.query.filter_by(status='GOOD STANDING').all()
        for instructor in instructors:
            # Checks if any of the instructor's courses have been canceled.
            # If any of their courses have been canceled, then they are issued a warning
            # If all of their courses have been canceled, then they are suspended.
            assigned_courses_count = instructor.courses.count()
            canceled_courses_count = instructor.courses.filter_by(status='CANCELED').count()
            if canceled_courses_count >= 1:
                issue_warning(instructor.id, 'You have at least one canceled course')  
            elif assigned_courses_count == canceled_courses_count:
                instructor.status = 'SUSPENDED'   

    elif school_info.current_period == 'class running':
        school_info.current_period = 'grading'

        students = Student.query.filter_by(special_registration=True).all()
        for student in students:
            student.special_registration = False
        
    elif school_info.current_period == 'grading':
        school_info.current_period = 'class set-up'
        
        grade_list = ['A', 'B', 'C', 'D', 'F']

        # issues warning to instructor if grading deadline missed
        instructors = Instructor.query.filter_by(status='GOOD STANDING').all()
        for instructor in instructors:
            assigned_courses = instructor.courses.all()
            missed_grading_deadline = False
            for course in assigned_courses:
                no_grade = course.students_enrolled.filter_by(semester=school_info.current_semester, grade=None).first()
                if no_grade:
                    missed_grading_deadline = True
            if missed_grading_deadline:
                issue_warning(instructor.id, 'Missed grading deadline')
        
        student_course_enrollment_no_grade = StudentCourseEnrollment.query.filter_by(grade=None).all()
        for enrollment in student_course_enrollment_no_grade:
            enrollment.grade = 'N'

        # determines avg rating of course
        courses = Course.query.all()
        for course in courses:
            reviews = course.reviews
            if reviews:
                review_rating = [review.rating for review in reviews]
                points = 0
                for rating in review_rating:
                    points += rating
                
                avg_rating = points / len(review_rating)
                course.avg_rating = avg_rating

                if avg_rating < 2:
                    
                    issue_warning(course.instructor.id, f'{course} average rating below 2')
        
        # determine course gpa
        '''
        courses = Course.query.filter(Course.status != 'CANCELED', Course.status != 'NOT SET').all()
        for course in courses:
            students_enrolled = course.students_enrolled.filter(StudentCourseEnrollment.semester == school_info.current_semester,
                                                                StudentCourseEnrollment.grade.in_(grade_list)).all()
            course_gpa_avg = calculate_gpa(students_enrolled)
            if course_gpa_avg > 3.5 or course_gpa_avg < 2.5:
                # insert code to have instructor be questioned by registrar
                pass
        '''

        # determine student gpa
        students = Student.query.filter_by(status='GOOD STANDING').all()
        for student in students:
            student_courses_enrolled_overall = student.courses_enrolled.filter(StudentCourseEnrollment.grade.in_(grade_list)).all()
            student_courses_enrolled_semester = student.courses_enrolled.filter(StudentCourseEnrollment.semester == school_info.current_semester,
                                                                                StudentCourseEnrollment.grade.in_(grade_list)).all()

            if student_courses_enrolled_overall:
                overall_gpa = calculate_gpa(student_courses_enrolled_overall)
                semester_gpa = calculate_gpa(student_courses_enrolled_semester)
                student.gpa = overall_gpa

                if overall_gpa < 2.0:
                    student.status = 'DISMISSED'
                elif overall_gpa >= 2.0 and overall_gpa <= 2.25:
                    issue_warning(student.id, 'Low GPA')
                elif semester_gpa > 3.75 or overall_gpa > 3.5:
                    student.honor_roll_count += 1            

        current_semester = school_info.current_semester
        year = current_semester[:4]
        season = current_semester[4:]

        if season == 'fall':
            season = 'spring'
            year = int(year) + 1
        else:
            season = 'fall'
        
        current_semester = str(year) + season
        school_info.current_semester = current_semester
        courses = Course.query.filter(Course.status != 'NOT SET').all()
        for course in courses:
            course.status = 'NOT SET'
        

    db.session.commit()
    return redirect(url_for('registrar_default_dash'))   


@app.route("/registrar_class_setup", methods=['POST', 'GET'])
@login_required
def registrar_class_setup():
    class_setup_form = ClassSetUpForm()

    if class_setup_form.validate_on_submit():
        existing_course = Course.query.filter_by(id=class_setup_form.course_code.data, status='OPEN').first()
        if existing_course:
            flash('Course already set up.', 'warning')
        else:
            start_time_data=class_setup_form.start_time.data
            end_time_data=class_setup_form.end_time.data
            overlap = False
            possible_overlap_course = Course.query.filter(Course.instructor_id==class_setup_form.instructor_name.data.id,
                                                          Course.day == class_setup_form.day.data,
                                                          Course.status == 'OPEN',
                                                          Course.id != class_setup_form.course_code.data).all()

            if possible_overlap_course:
                for course in possible_overlap_course:
                    if (((start_time_data >= course.start_time) and (start_time_data <= course.end_time)) or 
                        ((end_time_data >= course.start_time) and (end_time_data <= course.end_time))):
                        overlap = True

            if start_time_data > end_time_data:
                flash('Start time must be before end time', 'danger')
            elif overlap:
                flash('Overlapping section. Please double check instructor, times, and day', 'danger')
            else:
                existing_course = Course.query.filter_by(id=class_setup_form.course_code.data, status='NOT SET').first()
                if existing_course:
                    existing_course.capacity = class_setup_form.class_size.data
                    existing_course.start_time = class_setup_form.start_time.data
                    existing_course.end_time = class_setup_form.end_time.data
                    existing_course.day = class_setup_form.day.data
                    existing_course.instructor_id = class_setup_form.instructor_name.data.id
                    existing_course.status = 'OPEN'
                else:
                    course = Course(id=class_setup_form.course_code.data,
                                    course_name=class_setup_form.course_name.data.title(),
                                    capacity=class_setup_form.class_size.data,
                                    start_time=class_setup_form.start_time.data,
                                    end_time=class_setup_form.end_time.data,
                                    day=class_setup_form.day.data,
                                    instructor_id=class_setup_form.instructor_name.data.id,
                                    status='OPEN')
                    db.session.add(course)

                db.session.commit()
                flash('Course submitted successfully!', 'success')

        return redirect(url_for('registrar_class_setup'))

    return render_template('create_course_section.html', title='Class Set-up', class_setup_form=class_setup_form)


@app.route("/student_course_reg", methods=['POST', 'GET'])
@login_required
def student_course_reg():
    student_class_enroll_form = StudentClassEnrollForm()
    course_results = None
    student = Student.query.filter_by(id=current_user.id).first()
    courses_enrolled_query = student.courses_enrolled
    waitlist_joined_query = student.courses_waitlisted

    if student_class_enroll_form.validate_on_submit():
        if student_class_enroll_form.class_name.data and student_class_enroll_form.instructor_name.data:
            course_results = Course.query.filter(Course.id == student_class_enroll_form.class_name.data.id, 
                                                 Course.instructor_id == student_class_enroll_form.instructor_name.data.id,
                                                 Course.status != 'CANCELED',
                                                 Course.status != 'NOT SET').order_by(Course.start_time).all()
        
        elif student_class_enroll_form.class_name.data:
            course_results = Course.query.filter(Course.id == student_class_enroll_form.class_name.data.id,
                                                 Course.status != 'CANCELED',
                                                 Course.status != 'NOT SET').order_by(Course.start_time).all()

        elif student_class_enroll_form.instructor_name.data:
            course_results = Course.query.filter(Course.instructor_id == student_class_enroll_form.instructor_name.data.id,
                                                 Course.status != 'CANCELED',
                                                 Course.status != 'NOT SET').order_by(Course.start_time).all()

        else:
            course_results = Course.query.filter(Course.status != 'CANCELED', Course.status != 'NOT SET').order_by(Course.start_time).all()
        
    return render_template('enroll.html', title='Student Course Registration', form=student_class_enroll_form, 
                                                                               course_results=course_results,
                                                                               courses_enrolled=courses_enrolled_query,
                                                                               waitlist_joined=waitlist_joined_query)


@app.route("/student_course_reg/<int:index>", methods=['POST', 'GET'])
@login_required
def student_course_enroll(index):
    overlap = False
    course = Course.query.filter_by(id=index).first()
    student = Student.query.filter_by(id=current_user.id).first()
    course_already_taken = student.courses_enrolled.filter(StudentCourseEnrollment.course.has(id=course.id)).first()

    possible_overlap_courses = StudentCourseEnrollment.query.filter(StudentCourseEnrollment.student_id==current_user.id,
                                                                    StudentCourseEnrollment.course.has(day=course.day),
                                                                    or_(StudentCourseEnrollment.grade == None,    
                                                                        StudentCourseEnrollment.grade == 'F')) \
                                                            .join(Course).order_by(Course.start_time).all()

    if possible_overlap_courses:
            for c in possible_overlap_courses:
                if (((course.start_time >= c.course.start_time) and (course.start_time <= c.course.end_time)) or 
                    ((course.end_time >= c.course.start_time) and (course.end_time <= c.course.end_time))):
                    overlap=True

    if StudentCourseEnrollment.query.filter_by(student_id=current_user.id, grade=None).count() >= 3:
        flash('Already enrolled in 4 courses. Cannot enroll in anymore', 'warning')
    elif course_already_taken:
        flash('Already taken or currently enrolled in course. Please choose a different one', 'warning')
    elif overlap:
        flash("Can't enroll in course. Time conflicts with another course.", 'warning')
    else:
        current_semester = SchoolInfo.query.first().current_semester
        student_section_enrollment = StudentCourseEnrollment(student_id=current_user.id, course_id=index, semester=current_semester)
        course.number_enrolled += 1

        if course.number_enrolled == course.capacity:
            course.status = 'CLOSED'  

        db.session.add(student_section_enrollment)
        db.session.commit()
        flash('Enrolled in course successfully!', 'success')
    return redirect(url_for('student_course_reg'))


@app.route("/join_waitlist/<int:index>", methods=['POST', 'GET'])
@login_required
def join_waitlist(index):
    student_section_waitlisted = Waitlist(student_id=current_user.id, course_id=index)
    db.session.add(student_section_waitlisted)
    db.session.commit()
    flash('Waitlist joined', 'success')
    return redirect(url_for('student_course_reg'))


@app.route("/view_courses")
@login_required
def view_courses():
    valid_courses = Course.query.filter(Course.status != 'CANCELED', Course.status != 'NOT SET').all()
    canceled_courses = Course.query.filter_by(status='CANCELED')
    return render_template('view_courses.html', title='View Courses', valid_courses=valid_courses, canceled_courses=canceled_courses)


def issue_warning(user_id, warning):
    warning = Warning(user_id=user_id, warning=warning)
    db.session.add(warning)
    db.session.commit()


@app.route("/warned_stu_instr", methods=['POST', 'GET'])
@login_required
def warned_stu_instr():
    students = Student.query.filter(Student.status != 'DISMISSED', Student.status != 'GRADUATED').all()
    instructors = Instructor.query.all()
    warning_form = WarningForm()
    if warning_form.validate_on_submit():
        issue_warning(warning_form.warned_user.data.id, warning_form.warning_text.data.strip())
        flash('Warning created successfully!', 'success')
    return render_template('warned_stu_instr.html', title='Warnings', form=warning_form, students=students, instructors=instructors)


@app.route("/registrar_grading_period")
@login_required
def registrar_grading_period():
    return render_template('course_grading.html', title='Class Running')


@app.route("/student_dash/student_graduation")
@login_required
def student_graduation():
    courses_passed = StudentCourseEnrollment.query.filter(StudentCourseEnrollment.student_id==current_user.id, 
                                                          StudentCourseEnrollment.grade!=None,
                                                          StudentCourseEnrollment.grade!='F',
                                                          StudentCourseEnrollment.grade!='W').count()
    if courses_passed < 8:
        flash('Have not passed 8 courses yet. Warning issued', 'danger')
        warning_message = 'Reckless graduation application'
        issue_warning(current_user.id, warning_message)
    else:
        student = Student.query.filter_by(id=current_user.id)
        student.status = 'GRADUATED'
        db.session.commit()
        flash("Graduation application successfully submitted!", 'success')
    
    return redirect(url_for('student_dash'))


@app.route("/registrar_view_applicants")
@login_required
def registrar_view_applicants():
    
    instruc_apps = InstructorApplicant.query.filter().all()
    student_apps = StudentApplicant.query.filter().all()

    return render_template('view_applicants.html', title='View Applicants', 
                                                   student_applicants=student_apps,
                                                   instruc_applicants=instruc_apps)


@app.route("/student_app_accept/<int:index>")
@login_required
def student_app_accept(index):
    applicant = StudentApplicant.query.filter_by(id=index).first()

    generated_username = generate_username(applicant.first_name, applicant.last_name)
    generated_password = generate_password()
    hashed_password = bcrypt.generate_password_hash(generated_password).decode('utf-8')

    student_user = Student(username=generated_username,
                           email=applicant.email,
                           password=hashed_password,
                           first_name=applicant.first_name, 
                           last_name=applicant.last_name,
                           gpa=applicant.gpa,
                           type='student')

    response = {'application': 'accepted', 
                'type': 'student',
                'username': generated_username, 
                'password': generated_password}

    email_content = generate_email_content(response)

    send_email(applicant.email, email_content)

    db.session.add(student_user)
    db.session.delete(applicant)
    db.session.commit()

    student = Student.query.filter_by(username=generated_username).first()
    student.empl_id = student.id + 1000
    db.session.commit()
    return redirect(url_for('registrar_view_applicants'))


@app.route("/instruc_app_accept/<int:index>")
@login_required
def instruc_app_accept(index):
    applicant = InstructorApplicant.query.filter_by(id=index).first()

    ##########################################################################################
    ############# CREATE GENERATE INSTRUCTOR USERNAME ########################
    generated_username = generate_username(applicant.first_name, applicant.last_name)
    generated_password = generate_password()
    hashed_password = bcrypt.generate_password_hash(generated_password).decode('utf-8')

    instructor_user = Instructor(username=generated_username,
                                 email=applicant.email,
                                 password=hashed_password,
                                 first_name=applicant.first_name, 
                                 last_name=applicant.last_name,
                                 discipline=applicant.discipline,
                                 type='instructor')

    response = {'application': 'accepted',
                'type': 'instructor', 
                'username': generated_username, 
                'password': generated_password}

    email_content = generate_email_content(response)

    send_email(applicant.email, email_content)

    db.session.add(instructor_user)
    db.session.delete(applicant)
    db.session.commit()

    instructor = Instructor.query.filter_by(username=generated_username).first()
    instructor.empl_id = instructor.id + 1000
    db.session.commit()
    return redirect(url_for('registrar_view_applicants'))


@app.route("/instruc_app_delete/<int:index>")
@login_required
def instruc_app_delete(index):

    applicant = InstructorApplicant.query.filter_by(id=index).first()

    response = {'application': 'rejected'}
    email_content = generate_email_content(response)
    send_email(applicant.email, email_content)

    db.session.delete(applicant)
    db.session.commit()
    return redirect(url_for('registrar_view_applicants'))


@app.route("/student_app_delete/<int:index>", methods=['POST'])
@login_required
def student_app_delete(index):

    if request.method == 'POST':
        comment = request.form['rejectComment']
        #print(comment)
        applicant = StudentApplicant.query.filter_by(id=index).first()

        response = {'application': 'rejected', 'reason': comment}
        email_content = generate_email_content(response)
        send_email(applicant.email, email_content)

        db.session.delete(applicant)
        db.session.commit()
        return redirect(url_for('registrar_view_applicants'))

@app.route("/student_complaint", methods=['POST', 'GET'])
@login_required
def student_complaint():
    student_complaint_form = StudentComplaintForm()
    if student_complaint_form.validate_on_submit():
        complainee_user = User.query.filter_by(username=student_complaint_form.complainee_username.data, 
                                               type=student_complaint_form.user_type.data).first()
        if not complainee_user:
            flash('Input data does not match our records. Please double check', 'warning')
        elif complainee_user.id == current_user.id:
            flash('Cannot file complaint against yourself', 'warning')
        else:
            complaint = Complaint(complaint=student_complaint_form.complaint_text.data,
                                  complainee_id=complainee_user.id,
                                  filer_id=current_user.id)
            db.session.add(complaint)
            db.session.commit()
            flash('Complaint filed successfully. Registrar will review.', 'success')
        
    return render_template('student_complaint.html', title='Student Complaint', form=student_complaint_form)


@app.route("/instructor_complaint", methods=['POST', 'GET'])
@login_required
def instructor_complaint():
    instructor_complaint_form = InstructorComplaintForm()
    if instructor_complaint_form.validate_on_submit():
        print(instructor_complaint_form.student.data.id)
        instructor_complaint = Complaint(complaint=instructor_complaint_form.complaint_text.data,
                                         complainee_id=instructor_complaint_form.student.data.id,
                                         filer_id=current_user.id)
        db.session.add(instructor_complaint)
        db.session.commit()
        flash('Complaint created successfully!', 'success')
    return render_template('instructor_complaint.html', title='Instructor Complaint', form=instructor_complaint_form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))
