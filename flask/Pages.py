from flask import Flask, redirect, url_for

app = Flask(__name__)


@app.route("/")
def home():
    return "Home Page"

@app.route("/student_app")
def student_app():
    return "Student Application"

@app.route("/instructor_app")
def instructor_app():
    return "Instructor Application"

@app.route("/student_dash")
def student_dash():
    return "Student Dashboard"

@app.route("/instructor_dash")
def instructor_dash():
    return "Instructor Dashboard"

@app.route("/registrar_dash")
def registrar_dash():
    return "Registrar Dashboard"

@app.route("/<name>")
def user(name):
    return f"Hello {name}!"

@app.route("/admin")
def admin():
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run()
