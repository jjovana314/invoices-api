import exceptions
import pytz
import time
from http import HTTPStatus
from datetime import datetime, timezone
from json import load, dumps, loads
from jsonschema import ValidationError, validate
from config import invoices, liability_error, liability, format_issue_date
from resources.invoice_status import InvoiceStatus

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
            # if there is exception occurred
            if value in ex_str:
                # raise exceptions.schema_exceptions[idx](ex_str) from None
                raise exceptions.schema_exceptions[idx](
                    exceptions.error_messages[idx]
                ) from None


def schema_generator(data: dict, schema_file_name: str) -> None:
    """ Generate json schema for current data.

  Arguments:
    data {dict} -- data from user
    schema_file_name {str} -- file where schema is located
  """
    global schema
    schema_file_ext = f"schemas/{schema_file_name}.json"
    with open(schema_file_ext, "r") as f:
        schema = load(f)
    validate_schema(data)


def login_validation(server_data: dict) -> None:
    """ Validate login information for current user.

  Arguments:
    server_data {dict} -- data from user

  Raises:
    LoginException: if login data is not valid
  """
    if server_data.get("login") is None or server_data.get("password") is None:
        raise exceptions.LoginException


def generate_date_time() -> str:
    """ Generate date and time with timezone Europe/Belgrade. """
    tzone = pytz.timezone("Europe/Belgrade")
    time_with_zone = datetime.now(tzone)
    date_curr = time.localtime()

    return time_with_zone.isoformat()


def login_exception_handler(server_data: dict, counter: int) -> tuple:
    """ Handle LoginException from login_validation function.

  Arguments:
    server_data {dict} -- data from user
    counter {int} -- count how many times LoginException was raised

  Returns:
    Tuple with bool and counter value
    (False if exception occurred, True otherwise)
  """
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
        date_formatted = validate_date_time(format_issue_date, issue_date)
    except ValueError:
        liability_error["InvoiceNumber"].append(invoice_number)


def validate_schema_caller(data_validation: dict, schema_name: str) -> tuple:
    """ Call schema_generator function.

  Arguments:
    data_validation {dict} -- data for validation
    schema_name {str} -- name of file where schema is located (without extension)

  Returns:
    tuple with message and code
  """
    try:
        schema_generator(data_validation, schema_name)
    except exceptions.SchemaError as ex:
        return ex.args[0], HTTPStatus.BAD_REQUEST
    else:
        return "Data is valid", HTTPStatus.OK


def invalid_login_note() -> None:
    """ Write invalid login details in invalid_login_counter.txt file. """
    with open("invalid_login_counter.txt", "r") as f:
        invalid_login_counter = int(f.read())
    invalid_login_counter += 1
    with open("invalid_login_counter.txt", "w") as f:
        f.write(str(invalid_login_counter))


def validate_date_time(format_datetime: str, date_time: str) -> datetime:
    """ Date and time validation,

  Arguments:
    format_datetime {str} -- pattern for formatting
    date_time {str} -- date and time from user

  Returns:
    formatted datetime object
  """
    try:
        result = datetime.strptime(date_time, format_datetime)
    except ValueError:
        raise ValueError from None
    else:
        return result


def generate_idf(invoice_number: str) -> str:
    """ Creating invoice's IDF (id fakture - invoice's id)

  Arguments:
    invoice_number {str} -- invoice number from user

  Returns:
    generated invoice's id
  """
    invoice_num_split = invoice_number.split(" ")[1].split("/")
    return invoice_num_split[0] + invoice_num_split[1] + "F"


def is_invalid_status_invoice(status_curr_idf: int):
    """ Invoice status checking.

  Arguments:
    status_curr_idf {int} -- status of current invoice

  Returns:
    True if invoice is not valid, False if it is valid
  """
    return (status_curr_idf == InvoiceStatus.Canceled.code or
            status_curr_idf == InvoiceStatus.Settled.code or
            status_curr_idf == InvoiceStatus.Invalid.code)
