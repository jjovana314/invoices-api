import pytest
import requests
from http import HTTPStatus

url = "http://127.0.0.1:5000/api/login"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}


def test_login():
    data = {"login": "name", "password": "pass"}
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK


def test_fail_schema_name_login():
    data = {"password": "pass"}

    msg = {"Code": HTTPStatus.BAD_REQUEST, "Message": "Please enter all required fields"}

    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == msg


def test_fail_schema_password_login():
    data = {"username": "name"}

    msg = {"Code": HTTPStatus.BAD_REQUEST, "Message": "Please enter all required fields"}
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == msg
