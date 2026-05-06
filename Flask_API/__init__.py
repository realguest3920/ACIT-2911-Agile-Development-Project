import pymongo
from flask import Flask, render_template
from .marketplace import api_bp

MongoDBURL = "mongodb+srv://realguest_db_user:eHr283CHww8nLCwG@cluster0.qivfiwd.mongodb.net/"
maindb = pymongo.MongoClient(MongoDBURL)["AgileDevelopment"]

def create_app():
    app = Flask(__name__, template_folder="../templates")
    app.register_blueprint(api_bp)

    @app.route("/")
    def index() :
        listings = list(maindb["Listings"].find())
        return render_template("index.html", listings=listings)

    return app