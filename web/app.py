# from flask_restful import Resource, Api
from flask import Flask, jsonify, request
from flask_restful import Resource, Api
from pymongo import MongoClient
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from http import HTTPStatus
import exceptions
import login
import schema_validation
import register


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


liability = dict()
liability_error = dict()


class Register(Resource):
    """ Register invoices. """
    def post(self):
        global format_issue_date
        posted_data = request.get_json()    # this is list with dictionaries
        id_invoices = []
        max_invoices_request = 1000
        global liability
        global liability_error
        liability_error["InvoiceNumber"] = []
        liability["InvoiceNumber"] = []
        liability_error["LimitError"] = None
        liability_error["SchemaError"] = None

        result_dict = dict()
        idf_list = []

        if len(posted_data) > max_invoices_request:
            liability_error["LimitError"] = f"Invoice limit per request is {max_invoices_request}"

        for curr_invoice in posted_data:
            try:
                schema_validation.schema_generator(curr_invoice, "schema_register")
            except exceptions.SchemaError as ex:
                liability_error["SchemaError"] = ex.args[0]
            else:

                issue_date = curr_invoice["IssueDate"]
                invoice_number = curr_invoice["InvoiceNumber"]
                idf_list.append(invoice_number)

            if len(list(liability_error.values())) == 0:
                liability_error = None

            result_dict["liability"] = liability
            result_dict["liabilityError"] = liability_error
            result_dict["IDFList"] = idf_list
        return result_dict


def validate_date_caller(data: dict) -> None:
    """ Date validation and liability dictionaries update.

    Arguments:
        data {dict} -- server data
    """
    global liability
    global liability_error
    global format_issue_date
    issue_date = data["IssueDate"]
    invoice_number = data["InvoiceNumber"]

    try:
        date_formated = register.validate_date_time(format_issue_date, issue_date)
    except ValueError:
        liability_error["InvoiceNumber"].append(invoice_number)
    else:
        liability["InvoiceNumber"].append(invoice_number)


class Assign(Resource):
    """ Assign invoice. """
    def post(self):
        server_data = request.get_json()
        for invoice in server_data:
            try:
                schema_validation.schema_generator(invoice, "schema_assign")
            except exceptions.SchemaError:
                return jsonify("Message": "Schema is not valid", "Code": HTTPStatus.BAD_REQUEST)
        return jsonify("Message": "Data is valid", "Code": HTTPStatus.OK)


class CancelAssign(Resource):
    """ Cancel assignation. """
    def post(self):
        server_data = request.get_json()
        try:
            schema_validation.schema_generator(server_data, "schema_cancel_assign")
        except exceptions.SchemaError:
            return jsonify("Message": "Schema is not valid", "Code": HTTPStatus.BAD_REQUEST)
        return jsonify("Message": "Data is valid", "Code": HTTPStatus.OK)
        

api.add_resource(Login, "/api/login")
api.add_resource(Register, "/api/invoice/register")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
