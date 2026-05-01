import pymongo
from flask import current_app, jsonify, request
from . import api_bp

MongoDBURL = "SHARABLE MONGODB URL HERE"
maindb = pymongo.pymongo.MongoClient(MongoDBURL)

@api_bp.route("/status", methods=["GET"])
def status():
    return {"status": "ok"}

@api_bp.route("/data/<int:server_id>", methods=["GET"])
def get_server_by_id(server_id) :
    return {"server_Id" : server_id}, 200
    #if data :
    #    return data.to_dict()
    #else :
    #    return {"error" : "Server Not Found"}, 404 