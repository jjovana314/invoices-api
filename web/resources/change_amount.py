from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import validate_schema_caller
from config import invoices


class ChangeAmount(Resource):
    """ Change amount of invoice. """

    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_change_amount")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        if server_data["amount"] <= 0:
            return jsonify(
                {
                    "Message": "Amount cannot be negative number",
                    "Code": HTTPStatus.BAD_REQUEST
                }
            )
        invoice_id = server_data["invoiceId"]
        if not invoices.find_one({"invoiceId": invoice_id}):
            return jsonify({"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST})
        with open("last_amount.txt", "w") as f:
            # save last amount from database in file
            f.write(str(invoices.find_one({"invoiceId": invoice_id})["Amount"]))
        id_change = invoices.find_one({"invoiceId": invoice_id})["idChange"] + 1
        invoices.update_one(
            {"invoiceId": invoice_id},
            {"$set": {"Amount": server_data["amount"], "idChange": id_change}}
        )
        return jsonify(
            {"Message": "Amount updated successfully", "Code": HTTPStatus.OK, "id": id_change}
        )
