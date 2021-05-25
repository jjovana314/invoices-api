import exceptions
import pytz
import time
from http import HTTPStatus
from datetime import datetime, timezone


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
