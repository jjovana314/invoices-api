from http import HTTPStatus
from flask import jsonify, request
from flask_restful import Resource
from helper import (
    validate_schema_caller,
    invalid_login_note,
    login_exception_handler,
    generate_date_time
)
from flask_jwt_extended import create_access_token, create_refresh_token
from config import Unauthenticated, invalid_login_counter


class Login(Resource):
    """ Login class. """

    def post(self):
        posted_data = request.get_json()
        global invalid_login_counter
        message, code = validate_schema_caller(posted_data, "schema_login")
        if code != HTTPStatus.OK:
            # schema is not valid
            return jsonify({"Message": message, "Code": code})

        is_login_valid, invalid_login_counter = login_exception_handler(
            posted_data, invalid_login_counter
        )
        with open("invalid_login_counter.txt", "w") as f:
            f.write(str(invalid_login_counter))
        if not is_login_valid:
            invalid_login_note()

        if invalid_login_counter >= 3:
            return jsonify({"Message": "Wait one minute, then try again", "Code": Unauthenticated})

        access_token = create_access_token(identity=posted_data["login"], fresh=True)
        refresh_token = create_refresh_token(posted_data["login"])
        date_time = generate_date_time()

        return jsonify(
            {
                "creationTime": date_time,
                "accessToken": access_token,
                "refreshToken": refresh_token
            }
        )
