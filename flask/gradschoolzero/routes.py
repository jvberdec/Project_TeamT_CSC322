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

@app.route("/statistics_page", methods=['POST', 'GET'])
def statistics_page():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template("statistics_page.html")


@app.route("/student_dash")
@login_required
def student_dash():
    if current_user.is_authenticated and current_user.type == "student":
        period = SemesterPeriod.query.first()
        student = Student.query.filter_by(id=current_user.id).first()
        courses_taken = student.courses_enrolled.filter(StudentCourseEnrollment.grade != None).all()
        current_courses = student.courses_enrolled.filter(StudentCourseEnrollment.grade == None).all()
        warnings = student.warnings

        return render_template('student_dash.html', 
                               title='Student Dashboard', 
                               courses_taken=courses_taken, 
                               current_courses=current_courses,
                               warnings=warnings,
                               current_period=period)
    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))


@app.route("/instructor_dash", methods=['POST', 'GET'])
@login_required
def instructor_dash():
    if current_user.is_authenticated and current_user.type == "instructor":
        period = SemesterPeriod.query.first()
        semester_period = SemesterPeriod.query.first()
        current_semester_id = semester_period.semester_id
        instructor = Instructor.query.filter_by(id=current_user.id).first()

        return render_template('instructor_dash.html', 
                               title='Instructor Dashboard', 
                               instructor_sections=instructor.sections, 
                               current_semester_id=current_semester_id,
                               current_period=period)

    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))


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
    change_period_form = ChangePeriodForm()
    period = SemesterPeriod.query.first()
    if change_period_form.validate_on_submit():
        period.current_period = change_period_form.period.data
        db.session.commit()
        flash('Period changed successfully!', 'success')
    
    if current_user.is_authenticated and current_user.type == "registrar":
        return render_template('registrar_dash.html', title='Registrar Dashboard', current_period=period)
    else:
        flash("You're not allowed to view that page!", 'danger')
        return redirect(url_for('home'))      


@app.route("/registrar_default_dash/next_period", methods=['POST', 'GET'])
@login_required
def next_period():
    semester_period = SemesterPeriod.query.first()

    if semester_period.current_period == 'class set-up':
        semester_period.current_period = 'course registration'

    elif semester_period.current_period == 'course registration':
        semester_period.current_period = 'class running'

    elif semester_period.current_period == 'class running':
        semester_period.current_period = 'grading'
        
    elif semester_period.current_period == 'grading':
        semester_period.current_period = 'class set-up'

    db.session.commit()
    return redirect(url_for('registrar_default_dash'))   


@app.route("/registrar_class_setup", methods=['POST', 'GET'])
@login_required
def registrar_class_setup():
    create_course_form = CreateCourseForm()
    class_setup_form = ClassSetUpForm()
    
    if create_course_form.validate_on_submit():
        course = Course(id=create_course_form.course_code.data, course_name=create_course_form.course_name.data.strip())
        db.session.add(course)
        db.session.commit()

        flash('Course submitted successfully!', 'success')
        return redirect(url_for('registrar_class_setup'))

    if class_setup_form.validate_on_submit():
        start_time_data=class_setup_form.start_time.data
        end_time_data=class_setup_form.end_time.data
        overlap = False
        possible_overlap_section = CourseSection.query.filter_by(instructor_id=class_setup_form.instructor_name.data.id,
                                                                 day=class_setup_form.day.data).all()

        if possible_overlap_section:
            for section in possible_overlap_section:
                if (((start_time_data >= section.start_time) and (start_time_data <= section.end_time)) or 
                    ((end_time_data >= section.start_time) and (end_time_data <= section.end_time))):
                    overlap = True

        if start_time_data > end_time_data:
            flash('Start time must be before end time', 'danger')
        elif overlap:
            flash('Overlapping section. Please double check instructor, times, and day', 'danger')
        else:
            current_semester = SemesterPeriod.query.first()
            section = CourseSection(course_code=class_setup_form.course.data.id,
                                    section_size=class_setup_form.class_size.data,
                                    start_time=class_setup_form.start_time.data,
                                    end_time=class_setup_form.end_time.data,
                                    day=class_setup_form.day.data,
                                    semester_id=current_semester.id,
                                    instructor_id=class_setup_form.instructor_name.data.id)

            db.session.add(section)
            db.session.commit()
            flash('Course submitted successfully!', 'success')

        return redirect(url_for('registrar_class_setup'))

    return render_template('create_course_section.html', title='Class Set-up', create_course_form=create_course_form,  
                                                                               class_setup_form=class_setup_form)


@app.route("/student_course_reg", methods=['POST', 'GET'])
@login_required
def student_course_reg():
    student_class_enroll_form = StudentClassEnrollForm()
    section_results = None
    student = Student.query.filter_by(id=current_user.id).first()
    sections_enrolled_query = student.courses_enrolled
    waitlist_joined_query = student.courses_waitlisted
    current_semester_id = SemesterPeriod.query.first().semester_id

    if student_class_enroll_form.validate_on_submit():
        if student_class_enroll_form.class_name.data and student_class_enroll_form.instructor_name.data:
            section_results = CourseSection.query.filter_by(course_code=student_class_enroll_form.class_name.data.id, 
                                                            instructor_id=student_class_enroll_form.instructor_name.data.id,
                                                            semester_id=current_semester_id).order_by(CourseSection.start_time).all()
        
        elif student_class_enroll_form.class_name.data:
            section_results = CourseSection.query.filter_by(course_code=student_class_enroll_form.class_name.data.id,
                                                            semester_id=current_semester_id).order_by(CourseSection.start_time).all()

        elif student_class_enroll_form.instructor_name.data:
            section_results = CourseSection.query.filter_by(instructor_id=student_class_enroll_form.instructor_name.data.id,
                                                            semester_id=current_semester_id).order_by(CourseSection.start_time).all()

        else:
            section_results = CourseSection.query.filter_by(semester_id=current_semester_id).order_by(CourseSection.start_time).all()
        
    return render_template('enroll.html', title='Student Course Registration', form=student_class_enroll_form, 
                                                                               section_results=section_results,
                                                                               sections_enrolled=sections_enrolled_query,
                                                                               waitlist_joined=waitlist_joined_query)


@app.route("/student_course_reg/<int:index>", methods=['POST', 'GET'])
@login_required
def student_section_enroll(index):
    overlap = False
    section = CourseSection.query.filter_by(id=index).first()
    course_already_taken = StudentCourseEnrollment.query.filter(StudentCourseEnrollment.section.has(course_code=section.course_code)).first()

    possible_overlap_sections = StudentCourseEnrollment.query.filter(StudentCourseEnrollment.student_id==current_user.id,
                                                                     StudentCourseEnrollment.section.has(day=section.day),
                                                                     or_(StudentCourseEnrollment.grade == None,    
                                                                         StudentCourseEnrollment.grade == 'F')) \
                                                             .join(CourseSection).order_by(CourseSection.start_time).all()

    if possible_overlap_sections:
            for s in possible_overlap_sections:
                if (((section.start_time >= s.section.start_time) and (section.start_time <= s.section.end_time)) or 
                    ((section.end_time >= s.section.start_time) and (section.end_time <= s.section.end_time))):
                    overlap=True

    if StudentCourseEnrollment.query.filter_by(student_id=current_user.id, grade=None).count() >= 3:
        flash('Already enrolled in 4 courses. Cannot enroll in anymore', 'warning')
    elif course_already_taken:
        flash('Already taken or enrolled in course. Please choose a different one', 'warning')
    elif overlap:
        flash("Can't enroll in course. Time conflicts with another course.", 'warning')
    else:
        student_section_enrollment = StudentCourseEnrollment(student_id=current_user.id, course_section_id=index)
        section_enrollment_count = StudentCourseEnrollment.query.filter_by(course_section_id=index).count()

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


@app.route("/warned_stu_instr", methods=['POST', 'GET'])
@login_required
def warned_stu_instr():
    warning_form = WarningForm()
    if warning_form.validate_on_submit():
        warning = Warning(user_id=warning_form.warned_user.data.id, warning=warning_form.warning_text.data)
        db.session.add(warning)
        db.session.commit()
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
        warning = Warning(user_id=current_user.id, warning=warning_message)
        db.session.add(warning)
        db.session.commit()
    else:
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
