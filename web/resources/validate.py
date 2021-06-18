from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import validate_schema_caller, generate_idf, invoice_exist, is_invalid_status_invoice
from config import invoices
from resources.invoice_status import InvoiceStatus


class Validate(Resource):
    """ Validate settlment invoices. """
    def post(self):
        server_data = request.get_json()
        settlement = dict()
        settlement_error = dict()
        _bank_num = 840      # this value is constant
        result = []
        for settled_invoice in server_data:
            message, code = validate_schema_caller(settled_invoice, "schema_validate")
            if code != HTTPStatus.OK:
                settlement_error = {"Message": message, "Code": code}
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            if int(settled_invoice["bank"]) != _bank_num:
                settlement_error = {
                    "Message": f"Bank number can be only {_bank_num}",
                    "Code": HTTPStatus.BAD_REQUEST
                }
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            idf = generate_idf(settled_invoice["invoiceNumber"])
            if not invoice_exist("invoiceId", idf):
                settlement_error = {
                    "Message": f"Invoice with id {idf} does not exist",
                    "Code": HTTPStatus.BAD_REQUEST
                }
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            settled_amount = settled_invoice["settledAmount"]
            curr_idf = generate_idf(settled_invoice["invoiceNumber"])
            amount = invoices.find_one({"invoiceId": curr_idf})["Amount"]
            if settled_amount > amount:
                settlement_error = {
                    "Message": "setteled amount cannot be greather than invoice amount",
                    "Code": HTTPStatus.BAD_REQUEST
                }
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            status_curr_idf = invoices.find_one({"invoiceId": curr_idf})["Status"]
            if is_invalid_status_invoice(status_curr_idf):
                settlement_error = {
                    "Message": "Invoice is invalid or canceled or settled",
                    "Code": HTTPStatus.BAD_REQUEST
                }
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            settlement = {"invoiceId": curr_idf}
            result.append({"settlement": settlement, "settlementError": settlement_error})
        return jsonify(result)
