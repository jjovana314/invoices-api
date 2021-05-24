import pytest
import requests
from http import HTTPStatus


url = "http://127.0.0.1:5000"
path = f"{url}/api/login"


def test_login():
    data = """
    {
        "login": "name",
        "password": "pass"
    }
    """
    r = requests.post(path, data)
    assert r.status_code == 200


def test_fail_schema_name_login():
    data = """
    {
        "password: "pass"
    }
    """
    msg = {"Code": HTTPStatus.BAD_REQUEST, "Message": "Schema is not valid"}

    r = requests.post(path, data)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == msg


def test_fail_schema_password_login():
    data = """
    {
        "username": "name:
    }
    """
    msg = {"Code": HTTPStatus.BAD_REQUEST, "Message": "Schema is not valid"}
    r = requests.post(path, data)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == msg
