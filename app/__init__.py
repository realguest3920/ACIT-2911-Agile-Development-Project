import os
from flask import Flask
from config import Config
from flask_login import LoginManager
import pymongo

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), "..", "templates"),
    static_folder=os.path.join(os.path.dirname(__file__), "..", "static")
)
app.config.from_object(Config)
mongo = pymongo.MongoClient(app.config["MONGO_URI"])["AgileDevelopment"]
app.mongo = mongo
login = LoginManager(app)
login.login_view = 'login'
from app import routes