#The Marketplace is supposed to handle all the database management 
#and display product pages
from flask import Blueprint

api_bp = Blueprint("marketplace", __name__, url_prefix="/marketplace")

from . import routes
