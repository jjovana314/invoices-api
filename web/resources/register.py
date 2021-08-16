from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from resources.invoice_status import InvoiceStatus
from config import format_issue_date, invoices, liability, liability_error
from helper import validate_schema_caller, invoice_exist, validate_date_caller, generate_idf


max_invoices_request = 1000

liability_error["LimitError"] = None
liability_error["SchemaError"] = None


class Register(Resource):
  """ Register invoices. """
  def post(self):
    posted_data = request.get_json()    # this is list with dictionaries
    global liability
    global liability_error
    global max_invoices_request
    liability_error["InvoiceNumber"] = []
    liability["InvoiceNumber"] = []

    result_dict = dict()
    idf_list = []       # list with invoces id
    result_dict = validate_num_of_invoices(posted_data, result_dict)
    if len(result_dict.values()) == 0:
      for curr_invoice in posted_data:    # posted_data is a list
        message, code = validate_schema_caller(curr_invoice, "schema_register")
        if code != HTTPStatus.OK:
          # update liability_error dictionary
          liability_error["SchemaError"] = message
          liability_error["InvoiceNumber"].append(curr_invoice.get("InvoiceNumber"))
        else:
          # if data is valid
          validate_date_caller(curr_invoice)
          liability["InvoiceNumber"].append(curr_invoice.get("InvoiceNumber"))
          idf = generate_idf(curr_invoice["InvoiceNumber"])
          idf_list.append(idf)
          if invoice_exist("invoiceId", idf):
            return jsonify(
              {
                "Message": f"Invoice with id {idf} already exist",
                "Code": HTTPStatus.BAD_REQUEST
              }
            )
          curr_invoice["invoiceId"] = idf
          curr_invoice["Status"] = InvoiceStatus.Active.code
          curr_invoice["idChange"] = 0
          invoices.insert_one(curr_invoice)   # insert invoice in database

        if len(list(liability_error.values())) == 0:
          liability_error = None

        result_dict["liability"] = liability
        result_dict["liabilityError"] = liability_error
        result_dict["IDFList"] = idf_list
    return jsonify(result_dict)


def validate_num_of_invoices(posted_data: list, result_dict: dict) -> dict:
  global max_invoices_request
  global liability_error
  if len(posted_data) > max_invoices_request:
    liability_error["LimitError"] = f"Invoice limit per request is {max_invoices_request}"
    result_dict["liabilityError"] = liability_error
  return result_dict
