import os
from datetime import datetime
from wsgiref.validate import validator
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message


basedir = os.getcwd()

app = Flask(__name__)
# config for session
app.config['SECRET_KEY'] = 'jjjj'
# config for db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir + '//data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# config for mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_SENDER'] = os.getenv('MAIL_SENDER')
app.config['MAIL_PASSWORD'] = 'jtdrtfkwmgopescs'
# 啟用 smtp 新作法，參考 https://github.com/twtrubiks/Flask-Mail-example
# jtdrtfkwmgopescs

bootstrap = Bootstrap(app)
moment = Moment(app)
mail = Mail(app)

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    mail = StringField('Contact email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return f'<Role {self.name}>'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=True)
    email = db.Column(db.String(64), unique=True, nullable=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f'<User {self.username}>'


def welcome_mail(user_mail):
    subject = '【Flasky_Test】_Welcome'
    sender = app.config['MAIL_SENDER']
    msg = Message(subject, sender=sender, recipients=[user_mail])
    msg.html = '<h2>Welcome to the website.</h2>'
    mail.send(msg)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        old_name = session.get('name')
        if user == None:
            user = User(username=form.name.data)
            useremail = User(email=form.mail.data)
            db.session.add_all([user, useremail])
            db.session.commit()
            # session['name'] = form.name.data
            # session['usermail'] = form.mail.data
            session['know'] = False
            welcome_mail(useremail)
        else:
            session['know'] = True
        
        if old_name != None and old_name != form.name.data:
            flash('Look like you have changed your name!')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', current_time=datetime.utcnow(), form=form, name=session.get('name'),
                            know=session.get('know', False))



if __name__ == '__main__':
    app.run(debug=True)