import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_service import access
from storage import util
import os
from bson.objectid import ObjectId

server = Flask(__name__)

username = os.environ.get("MONGO_USERNAME")
password = os.environ.get("MONGO_PASSWORD")


mongo_video = PyMongo(
    server,
    uri="mongodb+srv://project_user:project_user@mongodb-cluster.hhz7bbb.mongodb.net/video?retryWrites=true&w=majority",
)

mongo_mp3 = PyMongo(
    server,
    uri="mongodb+srv://project_user:project_user@mongodb-cluster.hhz7bbb.mongodb.net/mp3s?retryWrites=true&w=majority",
)

gridfs_instance_videos = gridfs.GridFS(mongo_video.db)
gridfs_instance_mp3s = gridfs.GridFS(mongo_mp3.db)

"""
Now below connection object is the connection to the rabbitmq server
The pika.BlockingConnection function creates a "blocking" connection to the RabbitMQ server,
which means that the connection is established synchronously and the function will block (wait) until the connection is established. 
This is in contrast to a "non-blocking" connection,
which is established asynchronously and does not block the calling thread while the connection is being established.
"""
connection = pika.BlockingConnection(
    pika.ConnectionParameters("rabbitmq")
)  # This rabbitmq is the name of the rabbitmq container or the service name
channel = connection.channel()


@server.route("/login", methods=["POST"])
def login():
    """
    This function is used to login the user
    and this will interact with the auth_service.access.login function
    """

    request_from_flask = request
    """
    This request is from flask which is imported above.
    It represents the HTTP request made by the client (e.g., a web browser)
    and contains information about the request, such as the HTTP method (e.g., GET, POST), the URL, 
    the headers, and the body of the request.
    """
    token, error = access.login(request_from_flask)

    if not error:
        return token
    else:
        return error


@server.route("/register", methods=["POST"])
def register():
    """
    This function is used to register the user
    and this will interact with the auth_service.access.register function
    """

    request_from_flask = request
    """
    This request is from flask which is imported above.
    It represents the HTTP request made by the client (e.g., a web browser)
    and contains information about the request, such as the HTTP method (e.g., GET, POST), the URL, 
    the headers, and the body of the request.
    """
    token, error = access.register(request_from_flask)

    if not error:
        return token
    else:
        return error


@server.route("/upload", methods=["POST"])
def upload():
    access, error = validate.token(request)
    if error:
        return error
    access = json.loads(access)

    if access["admin"]:  # If user is authorized
        if len(request.files) == 0:
            return "No file provided", 400
        if len(request.files) > 1 or len(request.files) < 1:
            return "Exactly one file is required", 400

        for _, file in request.files.items():
            error = util.upload(file, gridfs_instance_videos, channel, access)

            if error:
                return error

        return "Success line 68", 200

    else:
        return "Not Authorized", 401


@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = gridfs_instance_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return f"internal server error{err}", 500

    return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
