from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import validate_schema_caller
from config import invoices


class RevertAmount(Resource):
    """ Revert amounts of invoice. """

    def post(self):
        server_data = request.get_json()
        message, code = validate_schema_caller(server_data, "schema_revert_amount")
        if code != HTTPStatus.OK:
            return jsonify({"Message": message, "Code": code})
        try:
            id_ = server_data["id"]
        except KeyError:
            return jsonify({"Message": "id is invalid", "Code": HTTPStatus.BAD_REQUEST})
        with open("last_amount.txt", "r") as f:
            last_amount = f.read()
        invoices.update_one({"idChange": id_}, {"$set": {"Amount": int(last_amount)}})
        return jsonify(
            {
                "Message": "Amount reverted successfully",
                "Code": HTTPStatus.OK,
                "last_amount": last_amount
            }
        )
