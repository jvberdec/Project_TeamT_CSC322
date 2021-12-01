from secrets import choice
from string import ascii_letters, digits, punctuation
import re
from flask import redirect, url_for, render_template, request, session, flash
from werkzeug.wrappers import response
from gradschoolzero import app, db, bcrypt, mail
from gradschoolzero.forms import (InstructorApplicationForm, StudentApplicationForm, LoginForm, 
                                  ClassSetUpForm, ChangePeriodForm, StudentClassEnrollForm, WarningForm, 
                                  StudentComplaintForm, InstructorComplaintForm, StudentGraduationForm, ChangePasswordForm)
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
        
        if response_dict.has_key('reason'):
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
        user = User.query.filter_by(username=login_form.username.data, type=login_form.user_type.data).first()
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



@app.route("/change_password")
def change_password():
    change_password_form = ChangePasswordForm()
    if change_password_form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(change_password_form.password.data).decode('utf-8')
        current_user.password = hashed_password
        current_user.logged_in_before = True
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
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
        student_applicant = StudentApplicant(first_name=student_app_form.first_name.data, 
                                             last_name=student_app_form.last_name.data,
                                             email=student_app_form.email.data, 
                                             dob=student_app_form.dob.data,
                                             gpa=student_app_form.gpa.data)
        db.session.add(student_applicant)
        db.session.commit()
        flash('Application filed successfully! You will be notified via email of our decision.', 'success')
        return redirect(url_for('login'))
    return render_template('student_app.html', title='Student Application', form=student_app_form)


@app.route("/instructor_app", methods=['POST', 'GET'])
def instructor_app():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
   
    instructor_app_form = InstructorApplicationForm()
    if instructor_app_form.validate_on_submit():
        instructor_applicant = InstructorApplicant(first_name=instructor_app_form.first_name.data, 
                                                   last_name=instructor_app_form.last_name.data,
                                                   email=instructor_app_form.email.data, 
                                                   dob=instructor_app_form.dob.data,
                                                   discipline=instructor_app_form.discipline.data)
        db.session.add(instructor_applicant)
        db.session.commit()
        flash('Application filed successfully! You will be notified via email of our decision.', 'success')
        return redirect(url_for('login'))

    return render_template('instructor_app.html', title='Instructor Application', form=instructor_app_form)

@app.route("/statistics_page", methods=['POST', 'GET'])
def statistics_page():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template("statistics_page.html")


@app.route("/student_dash")
#@login_required
def student_dash():
    return render_template('student_dash.html', title='Student Dashboard')


@app.route("/instructor_dash")
#@login_required
def instructor_dash():
    return render_template('instructor_dash.html', title='Instructor Dashboard')


@app.route("/registrar_default_dash", methods=['POST', 'GET'])
#@login_required
def registrar_default_dash():
    change_period_form = ChangePeriodForm()
    if change_period_form.validate_on_submit():
        flash('Period changed successfully!', 'success')
    return render_template('registrar_dash.html', title='Registrar Dashboard', form=change_period_form)


@app.route("/registrar_class_setup", methods=['POST', 'GET'])
#@login_required
def registrar_class_setup():
    class_setup_form = ClassSetUpForm()
    if class_setup_form.validate_on_submit():
        flash('Course submitted successfully!', 'success')
        return redirect(url_for('registrar_default_dash'))
    return render_template('create_course_section.html', title='Class Set-up', form=class_setup_form)

@app.route("/student_course_reg", methods=['POST', 'GET'])
#@login_required
def student_course_reg():
    student_class_enroll_form = StudentClassEnrollForm()
    if student_class_enroll_form.validate_on_submit():
        flash('Enrolled in course successfully!', 'success')
    return render_template('enroll.html', title='Student Course Registration', form=student_class_enroll_form)


# @app.route("/registrar_course_reg")
# #@login_required
# def registrar_course_reg():
#     return render_template('course_reg.html', title='Class Registration')

@app.route("/view_courses")
#@login_required
def view_courses():
    return render_template('view_courses.html', title='View Courses')


@app.route("/warned_stu_instr")
#@login_required
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
#@login_required
def registrar_grading_period():
    return render_template('course_grading.html', title='Class Running')

@app.route("/student_graduation")
#@login_required
def student_graduation():
    student_graduation_form = StudentGraduationForm()
    if student_graduation_form.validate_on_submit():
        flash("Form submitted successfully! You'll be notified with a decision. ", 'success')
    return render_template('graduation_form.html', title='Graduation Form', form=student_graduation_form)

@app.route("/registrar_view_applicants")
#@login_required
def registrar_view_applicants():
    
    instruc_apps = InstructorApplicant.query.filter().all()
    student_apps = StudentApplicant.query.filter().all()

    return render_template('view_applicants.html', title='View Applicants', 
                                                   student_applicants=student_apps,
                                                   instruc_applicants=instruc_apps)


@app.route("/student_app_accept/<int:index>")
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

    response = {'applicaion': 'accepted', 
                'type': 'student',
                'username': generated_username, 
                'password': generated_password}

    email_content = generate_email_content(response)

    send_email(applicant.email, email_content)

    db.session.add(student_user)
    db.session.delete(applicant)
    db.session.commit()

    return redirect(url_for('registrar_view_applicants'))


app.route("/instruc_app_accept/<int:index>")
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


@app.route("/instruc_app_delete/<int:index>")
def instruc_app_delete(index):

    applicant = InstructorApplicant.query.filter_by(id=index).first()

    response = {'application': 'rejected'}
    email_content = generate_email_content(response)
    send_email(applicant.email, email_content)

    db.session.delete(applicant)
    db.session.commit()
    return redirect(url_for('registrar_view_applicants'))


@app.route("/student_app_delete/<int:index>", methods=['POST'])
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
def student_complaint():
    student_complaint_form = StudentComplaintForm()
    if student_complaint_form.validate_on_submit():
        flash('Complaint created successfully!', 'success')
    return render_template('student_complaint.html', title='Student Complaint', form=student_complaint_form)


@app.route("/instructor_complaint")
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
