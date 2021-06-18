from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import validate_schema_caller, invoice_exist
from config import invoices


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
