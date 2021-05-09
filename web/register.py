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
    invoice_num_splited = invoice_number.split(" ")[1].split("/")
    return invoice_num_splited[0] + invoice_num_splited[1] + "F"

