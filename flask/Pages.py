import os
from dotenv import load_dotenv
from flask import Flask, redirect, url_for, render_template, request, session, flash
from forms import ApplicationForm, StudentApplicationForm, LoginForm
from datetime import timedelta
load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ['SECRET_KEY']


@app.route("/")
def home():
    # return "Home Page"
    return render_template("index.html")


@app.route("/login", methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        if login_form.user_type.data == 'student':
            flash('You have been logged in!', 'success')
            return redirect(url_for('student_dash'))
        elif login_form.user_type.data == 'instructor':
            return redirect(url_for('instructor_dash'))
        elif login_form.user_type.data == 'registrar':
            return redirect(url_for('registrar_default_dash'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=login_form)


@app.route("/student_app")
def student_app():
    student_app_form = StudentApplicationForm()
    return render_template('student_app.html', title='Student Application', form=student_app_form)


@app.route("/instructor_app")
def instructor_app():
    instructor_app_form = ApplicationForm()
    return render_template('instructor_app.html', title='Instructor Application', form=instructor_app_form)


@app.route("/student_dash")
def student_dash():
    return "Student Dashboard"


@app.route("/instructor_dash")
def instructor_dash():
    return "Instructor Dashboard"


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


if __name__ == "__main__":
    app.run(debug=True)
