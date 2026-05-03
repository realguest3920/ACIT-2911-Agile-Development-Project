from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_pymongo import PyMongo
app = Flask(__name__)
app.config.from_object(Config)
mongo = PyMongo(app)
login = LoginManager(app)
login.login_view = 'login'
from app import routes