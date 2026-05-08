import os
import pymongo
from app import app as web_app
from .marketplace import api_bp

MongoDBURL = "mongodb+srv://realguest_db_user:eHr283CHww8nLCwG@cluster0.qivfiwd.mongodb.net/"
maindb = pymongo.MongoClient(MongoDBURL)["AgileDevelopment"]

def create_app():
    if "marketplace" not in web_app.blueprints:
        web_app.register_blueprint(api_bp)
    return web_app