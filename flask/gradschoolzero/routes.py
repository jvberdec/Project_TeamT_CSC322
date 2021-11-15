from flask import redirect, url_for, render_template, request, session, flash
from gradschoolzero import app, db, bcrypt
from gradschoolzero.forms import InstructorApplicationForm, StudentApplicationForm, LoginForm
from gradschoolzero.models import *

@app.route("/")
@app.route("/home")
def home():
    # return "Home Page"
    return render_template("index.html")


@app.route("/login/", methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if login_form.user_type.data == 'student':
            return redirect(url_for('student_dash'))
        elif login_form.user_type.data == 'instructor':
            return redirect(url_for('instructor_dash'))
        elif login_form.user_type.data == 'registrar':
            return redirect(url_for('registrar_default_dash'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=login_form)


@app.route("/student_app", methods=['POST', 'GET'])
def student_app():
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
    instructor_app_form = InstructorApplicationForm()
    if instructor_app_form.validate_on_submit():
        instructor_applicant = InstructorApplicant(first_name=instructor_app_form.first_name.data, 
                                                   last_name=instructor_app_form.last_name.data,
                                                   email=instructor_app_form.email.data, 
                                                   dob=instructor_app_form.dob.data,
                                                   discipline=instructor_app_form.discipline.data)
        db.session.add(instructor_applicant)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('instructor_app.html', title='Instructor Application', form=instructor_app_form)

@app.route("/statistics_page", methods=['POST', 'GET'])
def statistics_page():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template("statistics_page.html")


@app.route("/student_dash")
def student_dash():
    return render_template('student_dash.html', title='Student Dashboard')


@app.route("/instructor_dash", methods=['POST', 'GET'])
def instructor_dash():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('instructor_dash.html', title='Instructor Dashboard')


@app.route("/registrar_default_dash")
def registrar_default_dash():
    return "Registrar Default Dashboard"


@app.route("/registrar_class_setup")
def registrar_class_setup():
    return "Registrar Class Set Up"


@app.route("/registrar_course_reg")
def registrar_course_reg():
    return "Registrar Course Registration"


@app.route("/registrar_class_run_period")
def registrar_class_run_period():
    return "Registrar Class Running Period"


@app.route("/registrar_grading_period")
def registrar_grading_period():
    return "Registrar Grading Period"


@app.route("/<name>")
def user(name):
    return f"Hello {name}!"


@app.route("/admin")
def admin():
    return redirect(url_for("home"))