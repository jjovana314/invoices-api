class InvoicesException(Exception):
    """ General invoice exception. """


class TokensException(InvoicesException):
    """ Raised if token is expired. """


class LoginException(InvoicesException):
    """ Raised if there is some isues with login data. """


class PasswordException(InvoicesException):
    """ Raised if password is not valid. """


class SchemaError(InvoicesException):
    """ General schema error. """


class TypeSchemaError(SchemaError):
    """ Raised if there is invalid type in data dictionary. """


class RequiredSchemaError(SchemaError):
    """ Raised if there is no required data in dictionary. """


schema_errors = ["Failed validating 'type' in schema", "Failed validating 'required' in schema"]

error_messages = ["Invalid type of data", "Please enter all required fields"]

schema_exceptions = [TypeSchemaError, RequiredSchemaError]
