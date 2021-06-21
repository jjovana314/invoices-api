from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import validate_schema_caller, generate_idf, invoice_exist, is_invalid_status_invoice
from config import invoices
from resources.invoice_status import InvoiceStatus



settlement_error = dict()
_bank_num = 840      # this value is constant


class Validate(Resource):
    """ Validate settlment invoices. """
    def post(self):
        server_data = request.get_json()
        settlement = dict()
        result = []
        global settlement_error
        global _bank_num
        for settled_invoice in server_data:
            message, code = validate_schema_caller(settled_invoice, "schema_validate")
            if code != HTTPStatus.OK:
                settlement_error = {"Message": message, "Code": code}
            else:
                validate_bank_num(settled_invoice)
                
                idf = generate_idf(settled_invoice["invoiceNumber"])
                update_settlement_error_if_invoice_exist(idf)
                
                settled_amount = settled_invoice["settledAmount"]
                curr_idf = generate_idf(settled_invoice["invoiceNumber"])
                amount = invoices.find_one({"invoiceId": curr_idf})["Amount"]
                validate_amount(settled_amount, amount)
                
                status_curr_idf = invoices.find_one({"invoiceId": curr_idf})["Status"]
                validate_status(status_curr_idf)
            if len(list(settlement_error.values())) > 0:
                return jsonify({"settlement": settlement, "settlementError": settlement_error})
            settlement = {"invoiceId": curr_idf}
            result.append({"settlement": settlement, "settlementError": settlement_error})
        return jsonify(result)


def validate_bank_num(settled_invoice: dict) -> None:
    """ Bank number validation.

    Arguments:
        settled_invoice {dict} -- current invoice
    """
    global settlement_error
    global _bank_num
    if int(settled_invoice["bank"]) != _bank_num:
        settlement_error = {"Message": f"Bank number can be only {_bank_num}", "Code": HTTPStatus.BAD_REQUEST}


def update_settlement_error_if_invoice_exist(idf: str) -> None:
    """ Check if invoice exist in database and update settlement_error.

    Arguments:
        idf {str} -- invoice id
    """
    global settlement_error
    if not invoice_exist("invoiceId", idf):
        settlement_error = {
            "Message": f"Invoice with id {idf} does not exist",
                "Code": HTTPStatus.BAD_REQUEST
            }


def validate_amount(settled_amount: int, amount: int) -> None:
    """ User's amount validation.

    Arguments:
        settled_amount {int} -- amount from database
        amount {int} -- amount from user
    """
    global settlement_error
    if settled_amount > amount:
        settlement_error = {
            "Message": "setteled amount cannot be greather than invoice amount",
            "Code": HTTPStatus.BAD_REQUEST
        }


def validate_status(status_curr_idf: int) -> None:
    """ Invoice status validation

    Arguments:
        setatus_curr_idf {int} -- current invoice status
    """
    if is_invalid_status_invoice(status_curr_idf):
        settlement_error = {
            "Message": "Invoice is invalid or canceled or settled",
            "Code": HTTPStatus.BAD_REQUEST
        }
