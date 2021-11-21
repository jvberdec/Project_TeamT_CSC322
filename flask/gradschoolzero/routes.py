import smtplib
from email.message import EmailMessage
from secrets import choice
from string import ascii_letters, digits, punctuation
from flask import redirect, url_for, render_template, request, session, flash
from gradschoolzero import app, db, bcrypt, EMAIL_ADDRESS, EMAIL_PASSWORD
from gradschoolzero.forms import InstructorApplicationForm, StudentApplicationForm, LoginForm
from gradschoolzero.forms import ClassSetUpForm, ChangePeriodForm, StudentClassEnrollForm, WarningForm
from gradschoolzero.models import *
from flask_login import login_user, current_user, logout_user, login_required


def password_generator():
    characters = ascii_letters + digits + punctuation
    password = ''.join(choice(characters) for i in range(32))

    return password


def send_email(recipient, content):
    msg = EmailMessage()
    msg['Subject'] = 'GradSchoolZero Admissions'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg.set_content(content)


    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


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
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)

            if login_form.user_type.data == 'student' and user.type == 'student':
                return redirect(url_for('student_dash'))
            elif login_form.user_type.data == 'instructor' and user.type == 'instructor':
                return redirect(url_for('instructor_dash'))
            elif login_form.user_type.data == 'registrar' and user.type == 'registrar':
                return redirect(url_for('registrar_default_dash'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=login_form)


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


@app.route("/instructor_dash", methods=['POST', 'GET'])
@login_required
def instructor_dash():
    if request.method == 'POST':
        return redirect(url_for('index'))
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
        flash('Enrolled in course successfully!', 'success')
    return render_template('warned_stu_instr.html', title='View Courses', form=warning_form)


# @app.route("/registrar_class_run_period")
# #@login_required
# def registrar_class_run_period():
#     return render_template('course_running.html', title='Class Running')


@app.route("/registrar_grading_period")
#@login_required
def registrar_grading_period():
    return render_template('course_grading.html', title='Class Running')

@app.route("/registrar_view_applicants")
#@login_required
def registrar_view_applicants():
    
    instruc_apps = InstructorApplicant.query.filter().all()
    student_apps = StudentApplicant.query.filter().all()

    return render_template('view_applicants.html', title='View Applicants', 
                                                   student_applicants = student_apps,
                                                   instruc_applicants=instruc_apps)


@app.route("/student_app_accept/<int:index>")
def student_app_accept(index):
    # applicant = StudentApplicant.query.filter_by(id=index).first()

    # # print(applicant.first_name)
    # # print(applicant.last_name)
    # # print(applicant.email)
    # # print(applicant.gpa)
    
    # student_user = Student(first_name=applicant.first_name, 
    #                         last_name=applicant.last_name,
    #                         email=applicant.email,
    #                         gpa=applicant.gpa)

    # db.session.add(student_user)
    # db.session.delete(applicant)
    # db.session.commit()
    return redirect(url_for('registrar_view_applicants'))


@app.route("/instruc_app_delete/<int:index>")
def instruc_app_delete(index):

    applicant = InstructorApplicant.query.filter_by(id=index).first()
    #print(applicant)
    db.session.delete(applicant)
    db.session.commit()
    return redirect(url_for('registrar_view_applicants'))


@app.route("/student_app_delete/<int:index>", methods=['POST'])
def student_app_delete(index):

    if request.method == 'POST':
        comment = request.form['rejectComment']
        #print(comment)
        applicant = StudentApplicant.query.filter_by(id=index).first()
        db.session.delete(applicant)
        db.session.commit()
        return redirect(url_for('registrar_view_applicants'))



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
