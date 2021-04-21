from json import load, dumps, loads
from jsonschema import ValidationError, validate
import exceptions


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
