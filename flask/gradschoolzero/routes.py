from secrets import choice
from string import ascii_letters, digits, punctuation
import re
from flask import redirect, url_for, render_template, request, session, flash
from werkzeug.wrappers import response
from gradschoolzero import app, db, bcrypt, mail
from gradschoolzero.forms import *
from gradschoolzero.models import *
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


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

@app.route("/statistics_page", methods=['POST', 'GET'])
def statistics_page():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template("statistics_page.html")


@app.route("/student_dash")
@login_required
def student_dash():
    if current_user.is_authenticated and current_user.type == "student":
        return render_template('student_dash.html', title='Student Dashboard')
    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))


@app.route("/instructor_dash")
@login_required
def instructor_dash():
    if current_user.is_authenticated and current_user.type == "instructor":
        return render_template('instructor_dash.html', title='Instructor Dashboard')
    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))

@app.route("/registrar_default_dash", methods=['POST', 'GET'])
@login_required
def registrar_default_dash():
    change_period_form = ChangePeriodForm()
    period = Period.query.first()
    if change_period_form.validate_on_submit():
        period.current_period = change_period_form.period.data
        db.session.commit()
        flash('Period changed successfully!', 'success')
    
    if current_user.is_authenticated and current_user.type == "registrar":
        return render_template('registrar_dash.html', title='Registrar Dashboard', form=change_period_form, current_period=period)
    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))

@app.route("/registrar_class_setup", methods=['POST', 'GET'])
@login_required
def registrar_class_setup():
    create_course_form = CreateCourseForm()
    create_semester_form = CreateSemesterForm()
    class_setup_form = ClassSetUpForm()
    
    if create_course_form.validate_on_submit():
        course = Course(id=create_course_form.course_code.data, course_name=create_course_form.course_name.data.strip())
        db.session.add(course)
        db.session.commit()

        flash('Course submitted successfully!', 'success')
        return redirect(url_for('registrar_class_setup'))

    if create_semester_form.validate_on_submit():
        semester = Semester(semester_name=create_semester_form.semester_name.data,
                            year=create_semester_form.start_date.data.year,
                            start_date=create_semester_form.start_date.data,
                            end_date=create_semester_form.end_date.data)

        db.session.add(semester)
        db.session.commit()

        flash('Semester submitted successfully!', 'success')
        return redirect(url_for('registrar_class_setup'))

    if class_setup_form.validate_on_submit():
        section = CourseSection(course_code=class_setup_form.course.data.id,
                                section_size=class_setup_form.class_size.data,
                                start_time=class_setup_form.start_time.data,
                                end_time=class_setup_form.end_time.data,
                                day=class_setup_form.day.data,
                                semester_id=class_setup_form.semester.data.id,
                                instructor_id=class_setup_form.instructor_name.data.id)

        db.session.add(section)
        db.session.commit()

        flash('Course submitted successfully!', 'success')

        return redirect(url_for('registrar_class_setup'))

    return render_template('create_course_section.html', title='Class Set-up', create_course_form=create_course_form, 
                                                                               create_semester_form=create_semester_form, 
                                                                               class_setup_form=class_setup_form)


@app.route("/student_course_reg", methods=['POST', 'GET'])
@login_required
def student_course_reg():
    student_class_enroll_form = StudentClassEnrollForm()
    section_results = None
    student = Student.query.filter_by(id=current_user.id).first()
    sections_enrolled_query = student.courses_enrolled
    waitlist_joined_query = student.courses_waitlisted

    if student_class_enroll_form.validate_on_submit():
        print(student_class_enroll_form.class_name.data)
        print(student_class_enroll_form.instructor_name.data)

        if student_class_enroll_form.class_name.data and student_class_enroll_form.instructor_name.data:
            section_results = CourseSection.query.filter_by(course_code=student_class_enroll_form.class_name.data.id, 
                                                            instructor_id=student_class_enroll_form.instructor_name.data.id).all()
        
        elif student_class_enroll_form.class_name.data:
            section_results = CourseSection.query.filter_by(course_code=student_class_enroll_form.class_name.data.id).all()

        elif student_class_enroll_form.instructor_name.data:
            section_results = CourseSection.query.filter_by(instructor_id=student_class_enroll_form.instructor_name.data.id).all()

        else:
            section_results=CourseSection.query.all() 
        
    return render_template('enroll.html', title='Student Course Registration', form=student_class_enroll_form, 
                                                                               section_results=section_results,
                                                                               sections_enrolled=sections_enrolled_query,
                                                                               waitlist_joined=waitlist_joined_query)


@app.route("/student_course_reg/<int:index>", methods=['POST', 'GET'])
@login_required
def student_section_enroll(index):
    student_section_enrollment = StudentCourseEnrollment(student_id=current_user.id, course_section_id=index)
    section_enrollment_count = StudentCourseEnrollment.query.filter_by(course_section_id=index).count()
    section = CourseSection.query.filter_by(id=index).first()
    if section_enrollment_count >= (section.section_size - 1):
        section.is_full = True
    db.session.add(student_section_enrollment)
    db.session.commit()
    flash('Enrolled in course successfully!', 'success')
    return redirect(url_for('student_course_reg'))


@app.route("/join_waitlist/<int:index>", methods=['POST', 'GET'])
@login_required
def join_waitlist(index):
    student_section_waitlisted = Waitlist(student_id=current_user.id, course_section_id=index)
    db.session.add(student_section_waitlisted)
    db.session.commit()
    flash('Waitlist joined', 'success')
    return redirect(url_for('student_course_reg'))


# @app.route("/registrar_course_reg")
# #@login_required
# def registrar_course_reg():
#     return render_template('course_reg.html', title='Class Registration')

@app.route("/view_courses")
@login_required
def view_courses():
    return render_template('view_courses.html', title='View Courses')


@app.route("/warned_stu_instr")
@login_required
def warned_stu_instr():
    warning_form = WarningForm()
    if warning_form.validate_on_submit():
        flash('Warning created successfully!', 'success')
    return render_template('warned_stu_instr.html', title='Warnings', form=warning_form)


# @app.route("/registrar_class_run_period")
# #@login_required
# def registrar_class_run_period():
#     return render_template('course_running.html', title='Class Running')


@app.route("/registrar_grading_period")
@login_required
def registrar_grading_period():
    return render_template('course_grading.html', title='Class Running')

@app.route("/student_graduation")
@login_required
def student_graduation():
    student_graduation_form = StudentGraduationForm()
    if student_graduation_form.validate_on_submit():
        flash("Form submitted successfully! You'll be notified with a decision. ", 'success')
    return render_template('graduation_form.html', title='Graduation Form', form=student_graduation_form)

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

    return redirect(url_for('registrar_view_applicants'))


@app.route("/instruc_app_accept/<int:index>")
@login_required
def instruc_app_accept(index):
    applicant = InstructorApplicant.query.filter_by(id=index).first()

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

@app.route("/student_complaint")
@login_required
def student_complaint():
    student_complaint_form = StudentComplaintForm()
    if student_complaint_form.validate_on_submit():
        flash('Complaint created successfully!', 'success')
    return render_template('student_complaint.html', title='Student Complaint', form=student_complaint_form)


@app.route("/instructor_complaint")
@login_required
def instructor_complaint():
    instructor_complaint_form = InstructorComplaintForm()
    if instructor_complaint_form.validate_on_submit():
        flash('Complaint created successfully!', 'success')
    return render_template('instructor_complaint.html', title='Instructor Complaint', form=instructor_complaint_form)



#------------------------------------------------------------------------------------
@app.route("/<name>")
@login_required
def user(name):
    return f"Hello {name}!"


@app.route("/admin")
@login_required
def admin():
    return 'admin'


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))
