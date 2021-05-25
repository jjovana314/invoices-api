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


def test_invalid_idf_format():
    invoice_id = "AA00"
    full_get_path = f"{path}/{invoice_id}"
    r = requests.get(full_get_path)
    response = {"code": 1, "message": "Unsuccess"}
    assert r.json()["status"] == response


def test_valid_id_liability():
    idf = "1923F"
    full_get_path = f"{path}/{idf}"
    r = requests.get(full_get_path)
    assert r.json()["liability"]["invoiceId"] == idf
    assert r.json()["status"]["code"] == 0


def test_multiple_requests():
    first_invoice = 16
    last_invoice = 21
    idf_list = [f"19{num}F" for num in range(first_invoice, last_invoice)]
    path_list = [f"{path}{idf}" for idf in idf_list]
    for idx_path_invoice in range(len(path_list)-1):
        r = requests.get(path_list[idx_path_invoice])
        assert r.json()["liability"]["invoiceId"] == idf_list[idx_path_invoice]
        assert r.json()["status"]["code"] == 0

