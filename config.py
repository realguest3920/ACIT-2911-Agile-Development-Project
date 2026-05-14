import os
import cloudinary
import cloudinary.uploader

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'guess_the_key'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb+srv://Anthony:Ri4NJgC1t3re97Dd@cluster0.qivfiwd.mongodb.net/AgileDevelopment'
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_USERNAME = 'agilemarketplace882@gmail.com'
    MAIL_PASSWORD = 'bwxr zcdv mfvf zrys'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True



cloudinary.config(
    cloud_name="dpt7onw0i",
    api_key="573919959662177",
    api_secret="oDZCoD9vLfr_QPrm2iq9LXesgZg",
    secure=True
)