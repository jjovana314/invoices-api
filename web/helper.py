import exceptions
import pytz
import time
from http import HTTPStatus
from datetime import datetime, timezone
from json import load, dumps, loads
from jsonschema import ValidationError, validate
from config import invoices, liability_error, liability, format_issue_date


schema = dict()


def validate_schema(server_data: dict) -> None:
    """ JSON schema validation.

    Arguments:
        server_data {dict} -- data from server

    Raises:
        SchemaError: if data dictionary is not valid
    """
    # we want json data, so we have to dump our data into json string
    # data = dumps(server_data)
    global schema
    try:
        # try to do validation for our json data
        validate(server_data, schema)
    except ValidationError as ex:
        ex_str = str(ex)
        for idx, value in enumerate(exceptions.schema_errors):
            # create appropriate message for user
            # if there is exception occured
            if value in ex_str:
                raise exceptions.schema_exceptions[idx](exceptions.error_messages[idx]) from None


def schema_generator(data: dict, schema_file_name: str) -> None:
    global schema
    schema_file_ext = schema_file_name + ".json"
    with open(schema_file_ext, "r") as f:
        schema = load(f)
    validate_schema(data)


def login_validation(server_data: dict) -> None:
    if server_data.get("login") is None or server_data.get("password") is None:
        raise exceptions.LoginException


def generate_date_time():
    tzone = pytz.timezone("Europe/Belgrade")
    time_with_zone = datetime.now(tzone)
    date_curr = time.localtime()

    return time_with_zone.isoformat()


def login_exception_handler(server_data: dict, counter: int) -> bool:
    try:
        login_validation(server_data)
    except exceptions.LoginException:
        counter += 1
        return False, counter
    else:
        return True, counter

def validate_date_caller(data: dict) -> None:
    """ Date validation and liability dictionaries update.

    Arguments:
        data {dict} -- server data
    """
    issue_date = data["IssueDate"]
    invoice_number = data["InvoiceNumber"]
    global format_issue_date

    try:
        date_formated = validate_date_time(format_issue_date, issue_date)
    except ValueError:
        liability_error["InvoiceNumber"].append(invoice_number)
    else:
        liability["InvoiceNumber"].append(invoice_number)


def validate_schema_caller(data_validation: dict, schema_name: str) -> tuple:
    """ Call schema_generator function.

    Arguments:
        data_validation {dict} -- data for validation
        shcema_name {str} -- name of file where schema is located (without extension)

    Returns:
        tuple with message and code
    """
    try:
        schema_generator(data_validation, schema_name)
    except exceptions.SchemaError:
        return "Schema is not valid", HTTPStatus.BAD_REQUEST
    else:
        return "Data is valid", HTTPStatus.OK


def invoice_exist(name_in_database: str, value: str) -> bool:
    """ Check invoice existance in database.

    Arguments:
        invoice_id {str} -- invoice id

    Returns:
        True if invoice exist in database, False otherwise
    """
    return invoices.count_documents({name_in_database: value}) != 0


def invalid_login_note():
    with open("invalid_login_counter.txt", "r") as f:
        invalid_login_counter = int(f.read())
    invalid_login_counter += 1
    with open("invalid_login_counter.txt", "w") as f:
        f.write(str(invalid_login_counter))


def validate_date_time(format_datetime: str, date_time: str) -> datetime:
    try:
        result = datetime.strptime(date_time, format_datetime)
    except ValueError:
        raise ValueError from None
    else:
        return result


def generate_idf(invoice_number):
    invoice_num_splited = invoice_number.split(" ")[1].split("/")
    return invoice_num_splited[0] + invoice_num_splited[1] + "F"
