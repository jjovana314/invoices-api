from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import validate_schema_caller, invoice_exist
from config import invoices


class PagedLiabilities(Resource):
    """ Show invoice data from database. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_paged_liabilities")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        if not invoice_exist("DebtorCompanyNumber", server_data["DebtorCompanyNumber"]):
            return jsonify({"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST})
        side_param = server_data["Side"]
        if side_param != "debtor" and side_param != "creditor":
            return jsonify(
                {
                    "Message": "Side parameter is not valid",
                    "Code": HTTPStatus.BAD_REQUEST
                }
            )
        server_data.pop("Side")     # remove Side value from data dictionary
        query_result = invoices.find(server_data)
        result = [invoice for invoice in query_result]
        for invoice in result:
            invoice["_id"] = str(invoice["_id"])
        return result
