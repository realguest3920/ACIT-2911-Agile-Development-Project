import pymongo
from datetime import datetime
from flask import current_app, jsonify, request
from . import api_bp

MongoDBURL = "mongodb+srv://realguest_db_user:eHr283CHww8nLCwG@cluster0.qivfiwd.mongodb.net/"
maindb = pymongo.MongoClient(MongoDBURL)["AgileDevelopment"]

@api_bp.route("/status", methods=["GET"])
def status():
    return {"status": "ok"}

@api_bp.route("/listings", methods=["GET"])
def show_all_listings() :
    listingsDB = maindb["Listings"].find()
    items = []
    for doc in listingsDB :
        tempDict = {
            "title": "?",
            "creator": "?",
            "description": "?",
            "views": "?",
            "likes": "?",
            "created_on": "?"
        }

        dockeys = doc.keys()
        for key in tempDict.keys() :
            if key in dockeys :
                tempDict[key] = doc[key]
        
        items.append(tempDict)
    return items, 200

#Get a specific listing
@api_bp.route("/listings/<int:item_id>", methods=["GET"])
def get_Listing(item_id) :
    listingsDB = maindb["Listings"]
    listing = listingsDB.find({"_id" : item_id})
    if listing :
        print(f"Found {item_id} in the database!")
        return listing
    else :
        return {"error": "listing does not exist"}, 404

#Create a new listing
@api_bp.route("/listings/create", methods=["POST"])
def create_Listing() :
    listingsDB = maindb["Listings"]
    data = request.get_json()

    tempDict = {
        "title": "?",
        "creator": "?",
        "description": "?",
        "views": "?",
        "likes": "?",
        "created_on": datetime.now()
    }

    dockeys = data.keys()
    for key in tempDict.keys() :
        if key in dockeys :
            tempDict[key] = data[key]
    
    listingsDB.insert_one(tempDict)

    return tempDict
