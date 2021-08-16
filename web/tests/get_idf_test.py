import pytest
import requests
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice"


def test_idf_ok():
  invoice_id = "2101F"
  full_get_path = f"{url}/{invoice_id}"
  r = requests.get(full_get_path)
  assert r.status_code == HTTPStatus.OK


def test_idf_not_exist():
  invoice_id = "1111F"
  full_get_path = f"{url}/{invoice_id}"
  r = requests.get(full_get_path)
  response = {"code": 1, "message": "Unsuccess"}
  assert r.json()["status"] == response


def test_invalid_idf_format():
  invoice_id = "AA00"
  full_get_path = f"{url}/{invoice_id}"
  r = requests.get(full_get_path)
  response = {"code": 1, "message": "Unsuccess"}
  assert r.json()["status"] == response


def test_valid_id_liability():
  idf = "2114F"
  full_get_path = f"{url}/{idf}"
  r = requests.get(full_get_path)
  assert r.json()["liability"]["invoiceId"] == idf
  assert r.json()["status"]["code"] == 0


def test_multiple_requests():
  first_invoice = 31
  last_invoice = 36
  idf_list = [f"21{num}F" for num in range(first_invoice, last_invoice)]
  path_list = [f"{url}/{idf}" for idf in idf_list]
  for idx_path_invoice in range(len(path_list)-1):
    r = requests.get(path_list[idx_path_invoice])
    assert r.json()["liability"]["invoiceId"] == idf_list[idx_path_invoice]
    assert r.json()["status"]["code"] == 0

