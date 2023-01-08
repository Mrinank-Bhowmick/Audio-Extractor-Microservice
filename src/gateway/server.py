import os, gridfs, pika , json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config["MONGO_URI"]="mongodb url"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

'''
Now below connection object is the connection to the rabbitmq server
The pika.BlockingConnection function creates a "blocking" connection to the RabbitMQ server,
which means that the connection is established synchronously and the function will block (wait) until the connection is established. 
This is in contrast to a "non-blocking" connection,
which is established asynchronously and does not block the calling thread while the connection is being established.
'''
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
    '''
    This function is used to login the user
    and this will interact with the auth_svc.access.login function
    '''
    
    request_from_flask = request
    '''
    This request is from flask which is imported above.
    It represents the HTTP request made by the client (e.g., a web browser)
    and contains information about the request, such as the HTTP method (e.g., GET, POST), the URL, 
    the headers, and the body of the request.
    '''
    token, error = access.login(request_from_flask)  
    
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