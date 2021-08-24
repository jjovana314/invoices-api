from http import HTTPStatus
from flask_restful import Resource
from flask import jsonify, request
from config import invoices
from helper import validate_schema_caller


class CancelAssign(Resource):
    """ Cancel assignation. """

    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_cancel_assign")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        invoice_id = server_data["InvoiceId"]
        if not invoices.find_one({"invoiceId": invoice_id}):
            return jsonify(
                {
                    "Message": f"Invoice with id {invoice_id} does not exist.",
                    "Code": HTTPStatus.BAD_REQUEST
                }
            )
        with open("last_debtor_company_number.txt", "r") as f:
            # read last debtor number from file
            debtor_number = f.read()
        invoices.update_one(
            {"invoiceId": server_data["InvoiceId"]},
            {"$set": {"DebtorCompanyNumber": debtor_number}}
        )
        return jsonify({"Message": "Assignation canceled successfully", "Code": HTTPStatus.OK})
