import os, gridfs, pika , json
from flask import Flask, requests
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config["MONGO_URI"]="mongodb url"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

Connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq")) # this is the connection to the rabbitmq server

channel = Connection.channel()

@server.route("/login", methods=["POST"])
def login():
    token, error = access.login(request)  # this request is from flask which is imported above and this is the request from the client
    
    if not error:
        return token
    else:
        return error

@server.route("/upload", methods=["POST"])
def upload():
    access,error = validate.token(request)
    access=json.loads(access)
    
    if access["admin"]:          # If user is authorized 
        if len(request.files) == 0:
            return "No file provided", 400
        if len(request.files) > 1 or len(request.files) < 1:
            return "Exactly one file is required", 400
        
        for _,file in request.files.items():
            error = util.upload(file,fs, channel, access)
            
            if error :
                return error
        
        return "Success", 200
    
    else:
        return "Not Authorized", 401 

@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0",port=8080)