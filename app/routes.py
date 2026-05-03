from flask import render_template, flash, redirect, url_for
from app import app, mongo
from flask_login import login_user, current_user
from app.forms import LoginForm, RegisterForm
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@app.route('/')
def index():
    if current_user.is_authenticated:
        return f'Logged in as {current_user.username}'
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    form = LoginForm()
    if form.validate_on_submit():
        user_data = mongo.db.users.find_one({"username": form.username.data})
    
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
        existing_user = mongo.db.users.find_one({"username": form.username.data})
        emailcheck = mongo.db.email.find_one({"email": form.username.data})
        if existing_user:
            flash('Username already exists')
        elif emailcheck:
            flash('Email already registered')
        else:
            hashed_password = generate_password_hash(form.password.data)
            mongo.db.users.insert_one({
                "username": form.username.data,
                "email": form.email.data,
                "password_hash": hashed_password,
                "created_at": datetime.now().strftime('%c')
            })
            flash('Account created successfully! Please log in.')
            return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)