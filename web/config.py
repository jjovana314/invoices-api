from pymongo import MongoClient
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api, Resource


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"
jwt = JWTManager(app)
api = Api(app)


mongo_client = MongoClient("mongodb://db:27017")
db = mongo_client.Database
invoices = db["Invoices"]
users = db["Users"]
assigned = db["Assigned"]

Unauthenticated = 401
format_issue_date = "%Y-%m-%d"
liability = dict()
liability_error = dict()
last_amount = 0
last_dbt_num = ""
invalid_login_counter = 0
