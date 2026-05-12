import pymongo
from datetime import datetime
from flask import current_app, jsonify, request
from . import api_bp
from app import mongo
import os
from flask import render_template, flash, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from config import Config
from app import app, mongo
s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

mail = Mail(app)

from app import app, mongo
from app.forms import LoginForm, RegisterForm
from app.models import User

maindb = mongo

def FindFirstNumber(dict) :
    minNum = 0
    ids = []
    for i in dict :
        if isinstance(i["_id"], int) :
            ids.append(i["_id"])
    
    ids.sort()

    for i in ids :
        if minNum == i :
            minNum += 1
        else :
            return minNum
    return minNum

@api_bp.route("/status", methods=["GET"])
def status():
    return {"status": "ok"}

@api_bp.route("/listings", methods=["GET"])
def show_all_listings() :
    listingsDB = maindb["Listings"].find()
    items = []
    for doc in listingsDB :
        items.append(doc) #This runs under the assumption that all data is correct
    
    return items, 200

#Get a specific listing
@api_bp.route("/listings/<int:item_id>", methods=["GET"])
def get_Listing(item_id) :
    listingsDB = maindb["Listings"]
    listing = listingsDB.find_one({"_id" : item_id})
    if listing :
        print(f"Found {item_id} in the database!")
        return listing
    else :
        return {"error": "listing does not exist"}, 404

#Create a new listing
@api_bp.route("/listings/create", methods=["POST"])
def create_Listing() :
    listingsDB = maindb["Listings"]
    data = request.get_json()

    title = data.get("title")
    creator = data.get("creator")
    price = data.get("price")
    condition = data.get("condition")
    description = data.get("description")
    if not title :
        return {"error" : "Missing required field: <title>"}, 400
    elif not creator :
        return {"error" : "Missing required field: <creator>"}, 400
    elif not price :
        return {"error" : "Missing required field: <price>"}, 400
    elif not condition :
        return {"error" : "Missing required field: <condition>"}, 400
    elif not description :
        return {"error" : "Missing required field: <description>"}, 400
    else :
        tempDict = {
            "_id": FindFirstNumber(listingsDB.find({}, {"_id": 1})),
            "title": title,
            "creator": creator,
            "price": price,
            "condition": condition,
            "description": description,
            "imgurl": "?",
            "views": 0,
            "likes": 0,
            "created_on": datetime.now()
        }
        listingsDB.insert_one(tempDict)

        return tempDict, 201
    

#Update a listing
@api_bp.route("/listings/update/<int:item_id>", methods=["PUT"])
def update_Listing(item_id) :
    listingsDB = maindb["Listings"]
    data = request.get_json()

    listing = listingsDB.find_one({"_id" : item_id})
    if listing:
        print(f"Found {item_id} in the database!")
        for key in data.keys() :
            if key in listing.keys() :
                listing[key] = data[key]
            else :
                return {"error": "One or more invalid Parameters"}, 400
        listingsDB.update_one({"_id" : item_id}, {"$set" : listing})
        return listing
    else :
        return {"error": "listing does not exist"}, 404

#Delete a listing
@api_bp.route("/listings/delete/<int:item_id>", methods=["DELETE"])
def delete_Listing(item_id) :
    listingsDB = maindb["Listings"]
    
    listing_exists = listingsDB.find_one({"_id" : item_id})
    if listing_exists :
        listingsDB.delete_one({"_id" : item_id})
        return {"success": "listing deleted"}, 200
    else:
        return {"error": "listing does not exist"}, 404
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
    mongo["users"].update_one({"email": email}, {"$set": {"confirmed": True}})
    return "successfully verified email"


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
