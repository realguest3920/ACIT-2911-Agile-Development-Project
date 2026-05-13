from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message
from itsdangerous import SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from app import app, mongo
from app.forms import LoginForm, RegisterForm
from app.models import User

api_bp = Blueprint("marketplace", __name__, url_prefix="/marketplace")

serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
mail = Mail(app)
maindb = mongo


def find_first_number(records):
    min_num = 0
    ids = []

    for record in records:
        if isinstance(record["_id"], int):
            ids.append(record["_id"])

    ids.sort()

    for item_id in ids:
        if min_num == item_id:
            min_num += 1
        else:
            return min_num

    return min_num


@app.route("/")
def index():
    listings = list(mongo["Listings"].find())
    return render_template("index.html", listings=listings)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data.lower().strip()
        user_data = mongo["users"].find_one(
            {
                "$or": [
                    {"username": identifier},
                    {"email": identifier},
                ]
            }
        )

        if user_data and check_password_hash(user_data["password_hash"], form.password.data):
            user_obj = User(user_data)
            login_user(user_obj, remember=form.remember.data)
            return redirect(url_for("index"))

        flash("Invalid username or password")

    return render_template("login.html", title="Login", form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        normalized_username = form.username.data.lower().strip()
        normalized_email = form.email.data.lower().strip()
        existing_user = mongo["users"].find_one({"username": normalized_username})
        email_check = mongo["users"].find_one({"email": normalized_email})

        if existing_user:
            flash("Username already exists")
        elif email_check:
            flash("Email already registered")
        else:
            hashed_password = generate_password_hash(form.password.data)
            mongo["users"].insert_one(
                {
                    "username": normalized_username,
                    "email": normalized_email,
                    "password_hash": hashed_password,
                    "created_at": datetime.now().strftime("%c"),
                    "confirmed": False,
                }
            )
            flash("Account created successfully! Please log in.")
            token = serializer.dumps(normalized_email, salt="email-confirm")

            message = Message(
                "Confirm Email",
                sender="agilemarketplace882@gmail.com",
                recipients=[normalized_email],
            )
            link = url_for("confirm_email", token=token, _external=True)
            message.body = f"Link for confirm {link}"
            mail.send(message)
            return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@app.route("/confirm_email/<token>")
def confirm_email(token):
    try:
        email = serializer.loads(token, salt="email-confirm", max_age=1000)
    except SignatureExpired:
        return "verification expired", 400

    flash("Email confirmed")
    mongo["users"].update_one({"email": email}, {"$set": {"confirmed": True}})
    return "successfully verified email"

@app.route("/listings/<int:item_id>")
def listing(item_id):
    listingsDB = mongo["Listings"]
    listing = listingsDB.find_one({"_id" : item_id})
    return render_template('listing.html', listing=listing)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@api_bp.route("/status", methods=["GET"])
def status():
    return {"status": "ok"}


@api_bp.route("/listings", methods=["GET"])
def show_all_listings():
    listings_db = maindb["Listings"].find()
    items = []

    for document in listings_db:
        items.append(document)

    return items, 200


@api_bp.route("/listings/<int:item_id>", methods=["GET"])
def get_listing(item_id):
    listings_db = maindb["Listings"]
    listing = listings_db.find_one({"_id": item_id})
    if listing:
        return listing

    return {"error": "listing does not exist"}, 404


@api_bp.route("/listings/create", methods=["POST"])
def create_listing():
    listings_db = maindb["Listings"]
    data = request.get_json()

    title = data.get("title")
    creator = data.get("creator")
    price = data.get("price")
    condition = data.get("condition")
    description = data.get("description")

    if not title:
        return {"error": "Missing required field: <title>"}, 400
    if not creator:
        return {"error": "Missing required field: <creator>"}, 400
    if not price:
        return {"error": "Missing required field: <price>"}, 400
    if not condition:
        return {"error": "Missing required field: <condition>"}, 400
    if not description:
        return {"error": "Missing required field: <description>"}, 400

    new_listing = {
        "_id": find_first_number(listings_db.find({}, {"_id": 1})),
        "title": title,
        "creator": creator,
        "price": price,
        "condition": condition,
        "description": description,
        "imgurl": "?",
        "views": 0,
        "likes": 0,
        "created_on": datetime.now(),
    }
    listings_db.insert_one(new_listing)

    return new_listing, 201


@api_bp.route("/listings/update/<int:item_id>", methods=["PUT"])
def update_listing(item_id):
    listings_db = maindb["Listings"]
    data = request.get_json()

    listing = listings_db.find_one({"_id": item_id})
    if listing:
        for key in data.keys():
            if key in listing.keys():
                listing[key] = data[key]
            else:
                return {"error": "One or more invalid Parameters"}, 400

        listings_db.update_one({"_id": item_id}, {"$set": listing})
        return listing

    return {"error": "listing does not exist"}, 404


@api_bp.route("/listings/delete/<int:item_id>", methods=["POST"])
def delete_listing(item_id):
    listings_db = maindb["Listings"]
    listing = listings_db.find_one({"_id": item_id})
    
    if listing:
        if current_user.is_authenticated and listing.get('creator') == current_user.username:
            listings_db.delete_one({"_id": item_id})
            flash("Listing deleted successfully!")
        else:
            flash("You are not authorized to delete this.")
    else:
        flash("Listing not found.")

    return redirect(url_for("index"))
