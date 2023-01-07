import jwt
import os
import datetime
from dotenv import load_dotenv
from flask import Flask,request
from flask_mysqldb import MySQL

load_dotenv()
 
server = Flask(__name__)
mysql=MySQL(server)

from configparser import ConfigParser

def read_db_config(filename='config_.ini', section='mysql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}  
    
    if parser.has_section('mysql'):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        print("Section {0} not found in the {1} file".format(section, filename))
    #else:
    #    raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db 

server.config['MYSQL_HOST']=db['mysql_host']
server.config['MYSQL_USER']=db['mysql_user']
server.config['MYSQL_PASSWORD']=db['mysql_password']
server.config['MYSQL_DB']=db['mysql_db']
server.config['MYSQL_PORT']=db['mysql_port']

def createJWT(username,secret,authz):               # authz will tell about admin: True/False
    return jwt.encode(
        {
            "username": username,
            "expression": datetime.datetime.utcnow() + datetime.timedelta(days=1), # expires in 1 day 
            "iat": datetime.datetime.utcnow(),
            "admin": authz
        },
        secret,
        algorithm="HS256")


@server.route('/login',methods=['POST'])
def login():
    auth=request.authorization
    if not auth :
        return "missing credentials",401
    
    # check db for username and password
    mysql_cursor = mysql.connection.cursor()
    result =mysql_cursor.execute(
        f"SELECT email,password FROM user WHERE email={auth.username}"
    )
    if result>0: # that means user exists in the database
        user_row=mysql_cursor.fetchone()
        email=user_row[0]
        password = user_row[1]
        
        if auth.username != email or auth.password != password:
            return "invalid credentials",401
        else:
            return createJWT(auth.username,os.getenv("JWT_SECRET"),True)
        
    else:
        return "Invalid credentials",401
    

@server.route("/validate",methods=['POST'])
def validate():
    
    encoded_JWT_token=request.headers.get('Authorization')
    
    if not encoded_JWT_token:
        return "missing token",401
    
    encoded_JWT_token = encoded_JWT_token.split(" ")[1]
    
    try:
        decoded_token = jwt.decode(encoded_JWT_token,os.getenv("JWT_SECRET"),algorithms=["HS256"])
    
    except:
        return "Not authorized",403
    
    return decoded_token,200
    
if __name__ == "__main__":
    
    server.run(host="0.0.0.0",port=5000,debug=True)