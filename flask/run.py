from gradschoolzero import app, db, bcrypt
from gradschoolzero.models import Semester, SemesterPeriod, User
from datetime import date

if __name__ == "__main__":
    db.create_all()
    registrar = User.query.filter_by(username='admin', type='registrar').first()
    semester_period = SemesterPeriod.query.first()

    if registrar is None:
        hashed_password = bcrypt.generate_password_hash(app.config['MAIL_PASSWORD']).decode('utf-8')
        registrar = User(username='admin',
                         email=app.config['MAIL_USERNAME'],
                         password=hashed_password,
                         first_name='',
                         last_name='',
                         type='registrar')
        db.session.add(registrar)
        db.session.commit()

    if semester_period is None:
        current_year = date.today().year
        if date.today() > date(current_year, 6, 30):
            current_semester_name = 'fall'
        else:
            current_semester_name = 'spring'
        current_semester = Semester(semester_name=current_semester_name, year=current_year)
        semester_period = SemesterPeriod(semester_id=1)
        db.session.add(current_semester)
        db.session.add(semester_period)
        db.session.commit()

    app.run(debug=True)
