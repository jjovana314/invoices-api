from datetime import datetime
from http import HTTPStatus


def validate_date_time(format_datetime: str, date_time: str) -> datetime:
    try:
        result = datetime.strptime(format_datetime, date_time)
    except ValueError:
        raise ValueError from None
    else:
        return result
