import ssl
import jwt
import datetime
import os

# load env
from dotenv import load_dotenv

load_dotenv()
from flask import Flask, request
import MySQLdb
from kubernetes import client, config

try:
    # If we're inside a pod, load the kubeconfig file from the environment.
    config.load_incluster_config()

except config.config_exception.ConfigException:
    # If we're not inside a pod, load the kubeconfig file.
    config.load_kube_config()


v1 = client.CoreV1Api()

# Here "auth-certificate" is the configmap in which the cacert.pem file is present
# and "mrinank-bhowmick" is the namespace

config_map = v1.read_namespaced_config_map("auth-certificate", "mrinank-bhowmick")
cacert_pem = config_map.data.get("cacert.pem")

server = Flask(__name__)

# MySQL SSL/TLS configuration
try:
    # print(cacert_pem)
    with open("cacert.pem", "w", encoding="utf-8") as f:
        f.write(cacert_pem)

    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.load_verify_locations(cafile="cacert.pem")


except Exception as e:
    print(f"Error loading CA certificate: {str(e)}")

try:
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.load_verify_locations(cafile="cacert.pem")
    ssl_context.check_hostname = False

    connection = MySQLdb.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        db=os.environ.get("MYSQL_DB"),
        port=int(os.environ.get("MYSQL_PORT")),
        ssl=ssl_context,
    )


except Exception as e:
    print(f"Error connecting to MySQL: {str(e)}")


@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    cur = connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0:
        user_row = cur.fetchone()
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "invalide credentials", 401


@server.route("/register", methods=["POST"])
def register():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401

    # check db for username and password
    cur = connection.cursor()
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0:
        return "user already exists", 401
    else:
        cur.execute(
            "INSERT INTO user (email, password) VALUES (%s, %s)",
            (auth.username, auth.password),
        )
        connection.commit()
        return "user created", 200


@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200


def createJWT(username, secret, authz):
    return jwt.encode(
        {
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
            + datetime.timedelta(days=1),
            "iat": datetime.datetime.utcnow(),
            "admin": authz,
        },
        secret,
        algorithm="HS256",
    )


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
