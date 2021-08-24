from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import validate_schema_caller, generate_idf, is_invalid_status_invoice
from config import invoices


_bank_num = 840  # this value is constant
# todo: post method needs to be refactored


class Validate(Resource):
    """ Validate settlement invoices. """

    def post(self):
        server_data = request.get_json()
        result = []
        global _bank_num
        for settled_invoice in server_data:
            message, code = validate_schema_caller(
                settled_invoice, "schema_validate"
            )
            if code == HTTPStatus.BAD_REQUEST:
                # settled_invoice["invoiceNumber"]  # expecting KeyError
                settlement_error = {"Message": message, "Code": code}
                settlement = {
                    "invoiceNumber": settled_invoice.get("invoiceNumber")
                }
            else:
                validate_bank_num(settled_invoice)

                idf = generate_idf(settled_invoice.get("invoiceNumber"))
                settlement_error = update_settlement_error_if_invoice_not_exist(idf)

                # if invoice exist in database
                if settlement_error is None:
                    settled_amount = settled_invoice["settledAmount"]
                    invoice_from_db = invoices.find_one({"invoiceId": idf})

                    amount = invoice_from_db["Amount"]
                    settlement_error = validate_amount(settled_amount, amount)
                    if settlement_error is None:
                        status_curr_idf = invoice_from_db["Status"]
                        settlement_error = validate_status(status_curr_idf)
                settlement = {"invoiceId": idf}
                if settlement_error is None:
                    invoices.update_one(
                        {"invoiceId": idf},
                        {"$set": {"validated": True}}
                    )

            result.append(
                {
                    "settlement": settlement,
                    "settlementError": settlement_error
                }
            )

        return jsonify(result)


def validate_bank_num(settled_invoice: dict) -> dict:
    """ Bank number validation.

  Arguments:
      settled_invoice {dict} -- current invoice
  """
    global _bank_num
    if int(settled_invoice["bank"]) != _bank_num:
        return {
            "Message": f"Bank number can be only {_bank_num}",
            "Code": HTTPStatus.BAD_REQUEST
        }


def update_settlement_error_if_invoice_not_exist(idf: str) -> dict:
    """ Check if invoice exist in database and update settlement_error.

  Arguments:
      idf {str} -- invoice id
  """
    if not invoices.find_one({"invoiceId": idf}):
        return {
            "Message": f"Invoice with id {idf} does not exist",
            "Code": HTTPStatus.BAD_REQUEST
        }


def validate_amount(settled_amount: int, amount: int) -> dict:
    """ User's amount validation.

  Arguments:
      settled_amount {int} -- amount from database
      amount {int} -- amount from user
  """
    if settled_amount > amount:
        return {
            "Message": "setteled amount cannot be greather than invoice amount",
            "Code": HTTPStatus.BAD_REQUEST
        }


def validate_status(status_curr_idf: int) -> dict:
    """ Invoice status validation

  Arguments:
      status_curr_idf {int} -- current invoice status
  """
    if is_invalid_status_invoice(status_curr_idf):
        return {
            "Message": "Invoice is invalid or canceled or settled",
            "Code": HTTPStatus.BAD_REQUEST
        }
