from gradschoolzero import app, db, bcrypt
from gradschoolzero.models import SchoolInfo, User
from datetime import date

if __name__ == "__main__":
    db.create_all()
    registrar = User.query.filter_by(username='admin', type='registrar').first()
    school_info = SchoolInfo.query.first()

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

    if school_info is None:
        current_year = date.today().year
        if date.today() > date(current_year, 6, 30):
            current_semester_season = 'fall'
        else:
            current_semester_season = 'spring'
        current_year = str(current_year)
        current_semester = current_year + current_semester_season
        school_info = SchoolInfo(current_period='class set-up', capacity=10, current_semester=current_semester)
        db.session.add(school_info)
        db.session.commit()

    app.run(debug=True)
