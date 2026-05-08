import os
from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

mail = Mail(app)

from app import app, mongo
from app.forms import LoginForm, RegisterForm
from app.models import User

@app.route("/")
def index():
    listings = list(mongo["Listings"].find())
    print(listings)
    return render_template("index.html", listings=listings)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data.lower().strip()
        user_data = mongo["users"].find_one({
            "$or": [
                {"username": identifier},
                {"email": identifier}
            ]
        })

        if user_data and check_password_hash(user_data['password_hash'], form.password.data):
            user_obj = User(user_data)
            login_user(user_obj, remember=form.remember.data)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')

    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        normalize = form.username.data.lower().strip()
        normemail = form.email.data.lower().strip()
        existing_user = mongo["users"].find_one({"username": normalize})
        emailcheck = mongo["users"].find_one({"email": normemail})
        if existing_user:
            flash('Username already exists')
        elif emailcheck:
            flash('Email already registered')
        else:
            hashed_password = generate_password_hash(form.password.data)
            mongo["users"].insert_one({
                "username": normalize,
                "email": normemail,
                "password_hash": hashed_password,
                "created_at": datetime.now().strftime('%c'),
                "confirmed": False
            })
            flash('Account created successfully! Please log in.')
            token = s.dumps(normemail, salt='email-confirm')
         
            msg = Message('Confirm Email', sender='agilemarketplace882@gmail.com',recipients=[normemail])

            link = url_for('confirm_email', token=token, _external = True )
            msg.body= 'Link for confirm {}'.format(link)
            mail.send(msg)
            return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=1000)
    except SignatureExpired:
        return "verifaction expired", 400
    
    flash("Email confirmed")
    mongo.db.users.update_one({"email": email}, {"$set": {"confirmed": True}})
    return "successfully verified email"


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
