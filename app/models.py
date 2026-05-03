from flask_login import UserMixin
from app import login, mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password_hash')


    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(id)})
    
    if not user_data:
        return None

    return User(user_data)
