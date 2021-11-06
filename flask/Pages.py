from flask import Flask, redirect, url_for, render_template, request, session
from forms import ApplicationForm, StudentAppplicationForm, LoginForm
from datetime import timedelta

app = Flask(__name__)


@app.route("/")
def home():
    # return "Home Page"
    return render_template("index.html")


@app.route("/login/", methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    return render_template('login.html', title='Login', form=login_form)


@app.route("/student_app")
def student_app():
    student_app_form = StudentAppplicationForm()
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
