import smtplib
from email.message import EmailMessage
from flask import redirect, url_for, render_template, request, session, flash
from gradschoolzero import app, db, bcrypt, EMAIL_ADDRESS, EMAIL_PASSWORD
from gradschoolzero.forms import InstructorApplicationForm, StudentApplicationForm, LoginForm
from gradschoolzero.models import *
from flask_login import login_user, current_user, logout_user, login_required


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
@login_required
def student_dash():
    return render_template('student_dash.html', title='Student Dashboard')


@app.route("/instructor_dash", methods=['POST', 'GET'])
@login_required
def instructor_dash():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('instructor_dash.html', title='Instructor Dashboard')


@app.route("/registrar_default_dash")
@login_required
def registrar_default_dash():
    return "Registrar Default Dashboard"


@app.route("/registrar_class_setup")
@login_required
def registrar_class_setup():
    return "Registrar Class Set Up"


@app.route("/registrar_course_reg")
@login_required
def registrar_course_reg():
    return "Registrar Course Registration"


@app.route("/registrar_class_run_period")
@login_required
def registrar_class_run_period():
    return "Registrar Class Running Period"


@app.route("/registrar_grading_period")
@login_required
def registrar_grading_period():
    return "Registrar Grading Period"


@app.route("/<name>")
@login_required
def user(name):
    return f"Hello {name}!"


@app.route("/admin")
@login_required
def admin():
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    logout_user()

