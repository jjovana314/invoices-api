from http import HTTPStatus
from flask_restful import Resource
from flask import jsonify, request
from helper import validate_schema_caller, invoice_exist
from resources.invoice_status import InvoiceStatus
from config import invoices


class Assign(Resource):
    """ Assign invoice. """
    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_assign")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        invoice_id = server_data["InvoiceId"]
        if not invoice_exist("invoiceId", invoice_id):
            return jsonify(
                {
                    "Message": f"Invoice with id {invoice_id} does not exist",
                    "Code": HTTPStatus.BAD_REQUEST
                }
            )
        with open("last_debtor_company_number.txt", "w") as f:
            # write in file old debtor number
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
