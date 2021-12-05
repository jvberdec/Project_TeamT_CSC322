from gradschoolzero import app, db, bcrypt
from gradschoolzero.models import Period, User, Instructor

if __name__ == "__main__":
    #drop just the instructor table
    # Instructor.__table__.drop(db.engine)

    #drop all tables
    #db.drop_all()
    db.create_all()
    registrar = User.query.filter_by(username='admin', type='registrar').first()
    period = Period.query.first()

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

    if period is None:
        period = Period()
        db.session.add(period)
        db.session.commit()

    app.run(debug=True)
