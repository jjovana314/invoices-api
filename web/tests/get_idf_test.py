import pytest
import requests
from http import HTTPStatus


url = "http://127.0.0.1:5000"
path = f"{url}/api/invoice/"


def test_idf_ok():
    invoice_id = "1918F"
    full_get_path = f"{path}/{invoice_id}"
    r = requests.get(full_get_path)
    assert r.status_code == HTTPStatus.OK


def test_idf_not_exist():
    invoice_id = "1111F"
    full_get_path = f"{path}/{invoice_id}"
    r = requests.get(full_get_path)
    response = {"code": 1, "message": "Unsuccess"}
    assert r.json()["status"] == response
