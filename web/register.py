from datetime import datetime
from http import HTTPStatus


def validate_date_time(format_datetime: str, date_time: str) -> datetime:
    try:
        result = datetime.strptime(date_time, format_datetime)
    except ValueError:
        raise ValueError from None
    else:
        return result


def generate_idf(invoice_number):
    return invoice_num.split(" ")[1].split("/")[0] + "F"
