from flask import Flask, jsonify, request
from flask_restful import Resource, Api, reqparse
from pymongo import MongoClient
from flask_jwt_extended import create_access_token, create_refresh_token, JWTManager
from http import HTTPStatus
import exceptions
import login
import schema_validation
import register
import enum


# todo: token should last only 20 minutes
# todo: test and refactor code


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret" # ! change this, only for testing
jwt = JWTManager(app)
api = Api(app)


mongo_client = MongoClient("mongodb://db:27017")
db = mongo_client.Database
invoices = db["Invoices"]
users = db["Users"]
assigned = db["Assigned"]

Unauthenticated = 401
invalid_login_counter = 0
format_issue_date = "%Y-%m-%d"


class InvoiceStatus(enum.Enum):
    """ Invoice status enum. """
    Active = (1, "Active registrated invoice")
    Invalid = (2, "The invoice was rejected by debtor")
    Canceled = (3, "The invoice was canceled by creditor")
    PartiallySettled = (4, "The invoice was partially settled in partial amount")
    Settled = (5, "The invoice has been settled")
    Assigned = (6, "The debtor assigned the invoice to another debtor")
    ProformaInvoice = (7, "Proforma invoice")

    def __new__(cls, member_value, member_message):
        member = object.__new__(cls)
        member._value = member_value
        member.message = member_message
        return member

    @property
    def code(self):
        return self._value


class InvoiceDetails(Resource):
    def get(self, idf):
        # todo: update this method
        status = dict()
        liability_invoice_details = dict()
        find_result = invoices.find_one({"invoiceId": idf})
        find_result["_id"] = str(find_result["_id"])
        # find_result = {"result": str(find_result)}
        return jsonify(find_result)


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
            result_dict["liabilityError"] = liability_error
            return result_dict
        for curr_invoice in posted_data:
            try:
                schema_validation.schema_generator(curr_invoice, "schema_register")
            except exceptions.SchemaError as ex:
                liability_error["SchemaError"] = ex.args[0]
                liability_error["InvoiceNumber"].append(curr_invoice.get("InvoiceNumber"))
            else:
                issue_date = curr_invoice["IssueDate"]
                liability["InvoiceNumber"].append(curr_invoice["InvoiceNumber"])
                idf_list.append(register.generate_idf(curr_invoice["InvoiceNumber"]))
                curr_invoice["invoiceId"] = register.generate_idf(curr_invoice["InvoiceNumber"])
                curr_invoice["Status"] = InvoiceStatus.Active.code
                invoices.insert(curr_invoice)

            if len(list(liability_error.values())) == 0:
                liability_error = None

        result_dict["liability"] = liability
        result_dict["liabilityError"] = liability_error
        result_dict["IDFList"] = idf_list
            
        return jsonify(result_dict)


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


def validate_schema_caller(data_validation: dict, schema_name: str) -> tuple:
    """ Call schema_generator function from schema_validation module.

    Arguments:
        data_validation {dict} -- data for validation
        shcema_name {str} -- name of file where schema is located (without extension)

    Returns:
        tuple with message and code
    """
    try:
        schema_validation.schema_generator(data_validation, schema_name)
    except exceptions.SchemaError:
        return "Schema is not valid", HTTPStatus.BAD_REQUEST
    else:
        return "Data is valid", HTTPStatus.OK


class Assign(Resource):
    """ Assign invoice. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_assign")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        curr_invoice_from_db = invoices.update_one(
            {"invoiceId": server_data["InvoiceId"]},
            {"$set": {"DebtorCompanyNumber": server_data["DebtorCompanyNumber"]}}
        )
        return jsonify({"Message": "Invoice assigned successfully", "Code": HTTPStatus.OK})


class CancelAssign(Resource):
    """ Cancel assignation. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_cancel_assign")
        return jsonify({"Message": message, "Code": code})


class Cancel(Resource):
    """ Cancel invoice. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_cancel")
        invoice_id = server_data["InvoiceId"]
        if not invoice_exist(invoice_id):
            return jsonify({"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST})
        invoices.remove({"invoiceId": invoice_id})
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        return jsonify({"Message": "Invoice removed successfully", "Code": HTTPStatus.OK})


class ChangeAmount(Resource):
    """ Change amount of invoice. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_change_amount")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        invoice_id = server_data["invoiceId"]
        if not invoice_exist(invoice_id):
            return jsonify({"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST})
        invoices.update({"invoiceId": invoice_id}, {"$set": {"Amount": server_data["amount"]}})
        return jsonify({"Message": "Amount updated successfully", "Code": HTTPStatus.OK})


def invoice_exist(invoice_id: str) -> bool:
    """ Check invoice existance in database.

    Arguments:
        invoice_id {str} -- invoice id

    Returns:
        True if invoice exist in database, False otherwise
    """
    return invoices.find({"invoiceId": invoice_id}).count() != 0


class PagedLiabilities(Resource):
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_paged_liabilities")
        if code != HTTPStatus.OK:
            return josnify({"Message": message, "Code": code})
        query_result = invoices.find(server_data)
        result = [invoice for invoice in query_result]
        for invoice in result:
            invoice["_id"] = str(invoice["_id"])
        return result


api.add_resource(Login, "/api/login")
api.add_resource(Register, "/api/invoice/register")
api.add_resource(Assign, "/api/invoice/assign")
api.add_resource(CancelAssign, "/api/invoice/cancel-assign")
api.add_resource(Cancel, "/api/invoice/cancel")
api.add_resource(InvoiceDetails, "/api/invoice/<string:idf>", endpoint="invoice")
api.add_resource(ChangeAmount, "/api/invoice/change-amount")
api.add_resource(PagedLiabilities, "/api/invoice/paged-liabilities")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
