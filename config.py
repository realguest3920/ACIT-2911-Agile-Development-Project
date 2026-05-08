import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'guess_the_key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://Anthony:Ri4NJgC1t3re97Dd@cluster0.qivfiwd.mongodb.net/AgileDevelopment'