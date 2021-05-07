from json import load, dumps, loads
from jsonschema import ValidationError, validate


data = [
    {
        "DebtorCompanyName": "10523",
        "InvoiceNumber": "Racun 18/01",
        "Amount": 1001,
        "Comments": "Komentar 1"
    },
    {
        "DebtorCompanyName": "10523",
        "InvoiceNumber": "Racun 18/02",
        "Amount": 1002.33,
        "IssueDate": "2018-02-28",
        "Comments": "Komentar 2",
        "Lifetime": 88
    }
]

with open("web/schema_register.json", "r") as f:
    schema = load(f)


class SchemaError(Exception):
    """ General schema error. """


class TypeSchemaError(SchemaError):
    """ Raised if there is invalid type in data dictionary. """


class RequiredSchemaError(SchemaError):
    """ Raised if there is no required data in dictionary. """


schema_errors = ["Failed validating 'type' in schema", "Failed validating 'required' in schema"]

error_messages = ["Invalid type of data", "Please enter all required fields"]

schema_exceptions = [TypeSchemaError, RequiredSchemaError]


def validate_schema(data) -> None:
    # we want json data, so we have to dump our data into json string
    # data = loads(data)
    global schema
    try:
        # try to do validation for our json data
        validate(data, schema)
    except ValidationError as ex:
        ex_str = str(ex)
        # print(ex_str)
        # print(schema_errors[1] in ex_str)
        for idx, value in enumerate(schema_errors):
            # create appropriate message for user
            # if there is exception occured
            if value in ex_str:
                raise schema_exceptions[idx](error_messages[idx]) from None


for dict_ in data:
    try:
        validate_schema(dict_)
    except SchemaError as ex:
        print(ex.args[0])
