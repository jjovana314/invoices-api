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
app.config["JWT_SECRET_KEY"] = "super-secret"
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
        member = object.__new__(cls)    # create new member object (InvoiceStatus member)
        member._value = member_value    # member value is code that we want to send
        member._message = member_message    # member message is message of InvoiceStatus ("Proforma invoice")
        return member

    @property
    def code(self):
        return self._value

    @property
    def message(self):
        return self._message


class InvoiceDetails(Resource):
    """ Return invoice details for given invoice id. """
    def get(self, idf):
        status = dict()
        if not invoice_exist("invoiceId", idf):
            status = {"message": "Unsuccess", "code": 1}
            return jsonify({"status": status})
        find_result = invoices.find_one({"invoiceId": idf})     # find invoice in database
        find_result["_id"] = str(find_result["_id"])        # convert _id element from database to string
        status = {"message": "Success", "code": 0}
        result = {"status": status, "liability": find_result}
        return jsonify(result)


class Login(Resource):
    """ Login class. """
    def post(self):
        posted_data = request.get_json()

        global invalid_login_counter
        message, code = validate_schema_caller(posted_data, "schema_login")
        if code != HTTPStatus.OK:
            # schema is not valid
            return jsonify({"Message": message, "Code": code})

        is_login_valid, invalid_login_counter = login.login_exception_handler(
            posted_data, invalid_login_counter
        )
        if not is_login_valid:
            with open("invalid_login_counter.txt", "r") as f:
                invalid_login_counter = f.read()
            invalid_login_counter += 1
            with open("invalid_login_counter.txt", "w") as f:
                f.write(str(invalid_login_counter))
        if invalid_login_counter >= 3:
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
last_amount = 0
last_dbt_num = ""


class Register(Resource):
    """ Register invoices. """
    def post(self):
        global format_issue_date
        posted_data = request.get_json()    # this is list with dictionaries
        max_invoices_request = 1000
        global liability
        global liability_error
        liability_error["InvoiceNumber"] = []
        liability["InvoiceNumber"] = []
        liability_error["LimitError"] = None
        liability_error["SchemaError"] = None

        result_dict = dict()
        idf_list = []       # list with invoces id
        if len(posted_data) > max_invoices_request:
            liability_error["LimitError"] = f"Invoice limit per request is {max_invoices_request}"
            result_dict["liabilityError"] = liability_error
            return result_dict
        for curr_invoice in posted_data:    # posted_data is a list
            message, code = validate_schema_caller(curr_invoice, "schema_register")
            if code != HTTPStatus.OK:
                # update liability_error dictionary
                liability_error["SchemaError"] = message
                liability_error["InvoiceNumber"].append(curr_invoice.get("InvoiceNumber"))
            else:
                # if data is valid
                issue_date = curr_invoice["IssueDate"]
                liability["InvoiceNumber"].append(curr_invoice["InvoiceNumber"])
                idf = register.generate_idf(curr_invoice["InvoiceNumber"])
                idf_list.append(idf)
                if invoice_exist("invoiceId", idf):
                    return jsonify({"Message": "Invoice already exist", "Code": HTTPStatus.BAD_REQUEST})
                curr_invoice["invoiceId"] = idf
                curr_invoice["Status"] = InvoiceStatus.Active.code
                curr_invoice["idChange"] = 0
                invoices.insert(curr_invoice)   # insert invoice in database

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
        if not invoice_exist("invoiceId", server_data["InvoiceId"]):
            return jsonify({"Message": "Invoice does not exist", "Code": HTTPStatus.BAD_REQUEST})
        global last_dbt_num
        with open("last_debtor_company_number.txt", "w") as f:
            f.write(invoices.find_one({"invoiceId": server_data["InvoiceId"]})["DebtorCompanyNumber"])
        curr_invoice_from_db = invoices.update_one(
            {"invoiceId": server_data["InvoiceId"]},
            {
                "$set": {
                    "DebtorCompanyNumber": server_data["DebtorCompanyNumber"],
                    "Status": InvoiceStatus.Assigned.code
                }
            }
        )
        return jsonify({"Message": "Invoice assigned successfully", "Code": HTTPStatus.OK})


class CancelAssign(Resource):
    """ Cancel assignation. """
    def post(self):
        # test post method
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_cancel_assign")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        invoice_id = server_data["InvoiceId"]
        if not invoice_exist("invoiceId", invoice_id):
            return jsonify({"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST})
        with open("last_debtor_company_number.txt", "r") as f:
            debtor_number = f.read()
        curr_invoice_from_db = invoices.update_one(
            {"invoiceId": server_data["InvoiceId"]},
            {"$set": {"DebtorCompanyNumber": debtor_number}}
        )
        return jsonify({"Message": "Assignation canceled successfully", "Code": HTTPStatus.OK})


class Cancel(Resource):
    """ Cancel invoice. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_cancel")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        invoice_id = server_data["InvoiceId"]
        if not invoice_exist("invoiceId", invoice_id):
            return jsonify({"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST})
        invoices.update_one(
            {"invoiceId": invoice_id},
            {"$set": {"Status": InvoiceStatus.Canceled.code}}
        )
        return jsonify({"Message": "Invoice removed successfully", "Code": HTTPStatus.OK})


class ChangeAmount(Resource):
    """ Change amount of invoice. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_change_amount")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        invoice_id = server_data["invoiceId"]
        if not invoice_exist("invoiceId", invoice_id):
            return jsonify({"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST})
        with open("last_amount.txt", "w") as f:
            f.write(str(invoices.find_one({"invoiceId": invoice_id})["Amount"]))
        id_change = invoices.find_one({"invoiceId": invoice_id})["idChange"] + 1
        invoices.update_one(
            {"invoiceId": invoice_id},
            {"$set": {"Amount": server_data["amount"], "idChange": id_change}}
        )
        return jsonify(
            {"Message": "Amount updated successfully", "Code": HTTPStatus.OK, "id": id_change}
        )


def invoice_exist(name_in_database: str, value: str) -> bool:
    """ Check invoice existance in database.

    Arguments:
        invoice_id {str} -- invoice id

    Returns:
        True if invoice exist in database, False otherwise
    """
    return invoices.find({name_in_database: value}).count() != 0


class PagedLiabilities(Resource):
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_paged_liabilities")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        if not invoice_exist("DebtorCompanyNumber", server_data["DebtorCompanyNumber"]):
            return jsonify({"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST})
        side_param = server_data["Side"]
        # todo: try to put this validation to jsonschema
        if side_param != "debtor" and side_param != "creditor":
            return jsonify({"Message": "Side parameter is not valid", "Code": HTTPStatus.BAD_REQUEST})
        server_data.pop("Side")
        query_result = invoices.find(server_data)
        result = [invoice for invoice in query_result]
        for invoice in result:
            invoice["_id"] = str(invoice["_id"])
        return result


class RevertAmount(Resource):
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_revert_amount")
        if code != HTTPStatus.OK:
            return jsonify({"Messge": message, "Code": code})
        try:
            id_ = server_data["id"]
        except KeyError:
            return jsonify({"Message": "id is invalic", "Code": HTTPStatus.BAD_REQUEST})
        with open("last_amount.txt", "r") as f:
            last_amount = f.read()
        invoices.update_one({"idChange": id_}, {"$set": {"Amount": int(last_amount)}})
        return jsonify(
            {
                "Message": "Amount reverted successfully", 
                "Code": HTTPStatus.OK, 
                "last_amount": last_amount
            }
        )


class Validate(Resource):
    """ Validate settlment invoices. """
    def post(self):
        server_data = request.get_json()
        settlement = dict()
        settlement_error = dict()
        bank_num = 840
        result = []
        for settled_invoice in server_data:
            message, code = validate_schema_caller(settled_invoice, "schema_validate")
            if code != HTTPStatus.OK:
                settlement_error = {"Message": message, "Code": code}
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            if int(settled_invoice["bank"]) != bank_num:
                settlement_error = {
                    "Message": f"Bank number can be only {bank_num}",
                    "Code": HTTPStatus.BAD_REQUEST
                }
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            idf = register.generate_idf(settled_invoice["invoiceNumber"])
            if not invoice_exist("invoiceId", idf):
                settlement_error = {"Message": "Invoice does not exist", "Code": HTTPStatus.BAD_REQUEST}
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            settled_amount = settled_invoice["settledAmount"]
            curr_idf = register.generate_idf(settled_invoice["invoiceNumber"])
            amount = invoices.find_one({"invoiceId": curr_idf})["Amount"]
            if settled_amount > amount:
                settlement_error = {
                    "Message": "setteled amount cannot be greather than invoice amount",
                    "Code": HTTPStatus.BAD_REQUEST
                }
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            status_curr_idf = invoices.find_one({"invoiceId": curr_idf})["Status"]
            if (status_curr_idf == InvoiceStatus.Canceled.code or
                status_curr_idf == InvoiceStatus.Settled.code or
                status_curr_idf == InvoiceStatus.Invalid.code):
                settlement_error = {
                    "Message": "Invoice is invalid or canceled or settled",
                    "Code": HTTPStatus.BAD_REQUEST
                }
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            settlement = {"invoiceId": curr_idf}
            result.append({"settlement": settlement, "settlementError": settlement_error})
        return jsonify(result)


api.add_resource(Login, "/api/login")
api.add_resource(Register, "/api/invoice/register")
api.add_resource(Assign, "/api/invoice/assign")
api.add_resource(CancelAssign, "/api/invoice/cancel-assign")
api.add_resource(Cancel, "/api/invoice/cancel")
api.add_resource(InvoiceDetails, "/api/invoice/<string:idf>", endpoint="invoice")
api.add_resource(ChangeAmount, "/api/invoice/change-amount")
api.add_resource(PagedLiabilities, "/api/invoice/paged-liabilities")
api.add_resource(RevertAmount, "/api/invoice/revert-amount")
api.add_resource(Validate, "/api/invoice/validate")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
