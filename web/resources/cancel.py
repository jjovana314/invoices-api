from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import validate_schema_caller, invoice_exist
from resources.invoice_status import InvoiceStatus
from config import invoices


class Cancel(Resource):
    """ Cancel invoice. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_cancel")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        invoice_id = server_data["InvoiceId"]
        if not invoice_exist("invoiceId", invoice_id):
            return jsonify(
                {
                    "Message": f"Invoice with id {invoice_id} does not exist.",
                    "Code": HTTPStatus.BAD_REQUEST
                }
            )
        invoices.update_one(
            {"invoiceId": invoice_id},
            {"$set": {"Status": InvoiceStatus.Canceled.code}}
        )
        return jsonify({"Message": "Invoice canceled successfully", "Code": HTTPStatus.OK})
