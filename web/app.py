# from flask_restful import Resource, Api
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
import login
import schema_validation


# todo: token should last only 20 minutes


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret" # ! change this, only for testing
jwt = JWTManager(app)
api = Api(app)


mongo_client = MongoClient("mongodb://db:27017")
db = mongo_client.Database
invoices = db["Invoices"]
users = db["Users"]

Unauthenticated = 401
invalid_login_counter = 0
format_issue_date = "%Y-%m-%d"


class Login(Resource):
    """ Login class. """
    def post(self):
        posted_data = request.get_json()

        global invalid_login_counter
        schema_validation(posted_data, "schema_login")

        is_login_valid, invalid_login_counter = login.login_exception_handler(posted_data, invalid_login_counter)
        if not is_login_valid and invalid_login_counter >= 3:
            # todo: if invalid_login_counter is greather than 3 we should forbid user to login next 1 minute
            return jsonify({"Message": "Wait one minute, then try again", "Code": Unauthenticated})

        access_token = create_access_token(identity=posted_data["login"], fresh=True)
        refresh_token = create_refresh_token(posted_data["login"])
        date_time = login.generate_date_time()
        # rfsh_token = login.generate_refresh_token()

        return jsonify(
            {
                "creationTime": date_time,
                "accessToken": access_token,
                "refreshToken": refresh_token
            }
        )

    # we should return token, date and time and refresh token


class Register(Resource):
    def post(self):
        global format_issue_date
        posted_data = request.get_json()    # this is list with dictionaries
        id_invoices = []
        result_dict = dict()
        liability = dict()
        liability_error = dict()        # this is null if we got no errors
        for curr_invoice in posted_data:
            schema_validation.schema_generator(curr_invoice, "schema_register")
            issue_date = curr_invoice.get("IssueDate")

            try:
                date_formated = validate_date_time(format_issue_date, issue_date)
            except ValueError as ex:
                liability_error["InvoiceNumber"] = curr_invoice.get("InvoiceNumber")
            else:
                id_invoices.append(curr_invoice.get("InvoiceNumber"))

        


api.add_resource(Login, "/api/login")
api.add_resource(Register, "/api/invoice/register")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
