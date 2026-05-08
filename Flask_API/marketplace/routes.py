import pymongo
from datetime import datetime
from flask import current_app, jsonify, request
from . import api_bp
from app import mongo

maindb = mongo

def FindFirstNumber(dict) :
    minNum = 0
    ids = []
    for i in dict :
        if isinstance(i["_id"], int) :
            ids.append(i["_id"])
    
    ids.sort()

    for i in ids :
        if minNum == i :
            minNum += 1
        else :
            return minNum
    return minNum

@api_bp.route("/status", methods=["GET"])
def status():
    return {"status": "ok"}

@api_bp.route("/listings", methods=["GET"])
def show_all_listings() :
    listingsDB = maindb["Listings"].find()
    items = []
    for doc in listingsDB :
        items.append(doc) #This runs under the assumption that all data is correct
    
    return items, 200

#Get a specific listing
@api_bp.route("/listings/<int:item_id>", methods=["GET"])
def get_Listing(item_id) :
    listingsDB = maindb["Listings"]
    listing = listingsDB.find_one({"_id" : item_id})
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

    title = data.get("title")
    creator = data.get("creator")
    price = data.get("price")
    condition = data.get("condition")
    description = data.get("description")
    if not title :
        return {"error" : "Missing required field: <title>"}, 400
    elif not creator :
        return {"error" : "Missing required field: <creator>"}, 400
    elif not price :
        return {"error" : "Missing required field: <price>"}, 400
    elif not condition :
        return {"error" : "Missing required field: <condition>"}, 400
    elif not description :
        return {"error" : "Missing required field: <description>"}, 400
    else :
        tempDict = {
            "_id": FindFirstNumber(listingsDB.find({}, {"_id": 1})),
            "title": title,
            "creator": creator,
            "price": price,
            "condition": condition,
            "description": description,
            "imgurl": "?",
            "views": 0,
            "likes": 0,
            "created_on": datetime.now()
        }
        listingsDB.insert_one(tempDict)

        return tempDict, 201
    

#Update a listing
@api_bp.route("/listings/update/<int:item_id>", methods=["PUT"])
def update_Listing(item_id) :
    listingsDB = maindb["Listings"]
    data = request.get_json()

    listing = listingsDB.find_one({"_id" : item_id})
    if listing:
        print(f"Found {item_id} in the database!")
        for key in data.keys() :
            if key in listing.keys() :
                listing[key] = data[key]
            else :
                return {"error": "One or more invalid Parameters"}, 400
        listingsDB.update_one({"_id" : item_id}, {"$set" : listing})
        return listing
    else :
        return {"error": "listing does not exist"}, 404

#Delete a listing
@api_bp.route("/listings/delete/<int:item_id>", methods=["DELETE"])
def delete_Listing(item_id) :
    listingsDB = maindb["Listings"]
    
    listing_exists = listingsDB.find_one({"_id" : item_id})
    if listing_exists :
        listingsDB.delete_one({"_id" : item_id})
        return {"success": "listing deleted"}, 200
    else:
        return {"error": "listing does not exist"}, 404
    