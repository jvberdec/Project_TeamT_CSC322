from gradschoolzero import app, db, bcrypt
from gradschoolzero.models import User

if __name__ == "__main__":
    db.create_all()
    registrar = User.query.filter_by(username='admin', type='registrar').first()
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
    app.run(debug=True)
