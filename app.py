import os
from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)

# Configure MongoDB connection URI
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/marketplace_db")
mongo = PyMongo(app)

@app.route("/")
def index():
    # Fetch all listings from the 'listings' collection in MongoDB
    # If the collection is empty, this returns an empty list
    listings = list(mongo.db.listings.find())
    
    # Pass the listings data to the template
    return render_template("index.html", listings=listings)

if __name__ == "__main__":
    app.run(debug=True)