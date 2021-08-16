import pytest
import requests
from json import dumps, loads
from http import HTTPStatus
from random import randint


url = "http://127.0.0.1:5000/api/invoice/change-amount"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_change_amount_ok():
  invoice_id = "2101F"
  amount = 500
  comments = "Comment 1"
  data = {"invoiceId": invoice_id, "amount": amount, "comments": comments}
  status_response = HTTPStatus.OK
  message = "Amount updated successfully"
  r = requests.post(url, json=data, headers=headers)
  assert r.json()["Message"] == message
  assert r.json()["Code"] == status_response


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_change_amount_ok_multiple():
  first_invoice = 10
  last_invoice = 15
  start_amount = 5000
  end_amount = 5005
  invoice_ids = [f"20{num}F" for num in range(first_invoice, last_invoice)]
  comments = [f"Comment {idx}" for idx in range(first_invoice, last_invoice)]
  status_response = HTTPStatus.OK
  message = "Amount updated successfully"
  for idx in range(len(invoice_ids)-1):
    amount = randint(start_amount, end_amount)
    data = {"invoiceId": invoice_ids[idx], "amount": amount, "comments": comments[idx]}
    r = requests.post(url, json=data, headers=headers)
    assert r.json()["Message"] == message
    assert r.json()["Code"] == status_response


def test_change_amount_invalid_multiple():
  first_invoice = 10
  last_invoice = 15
  start_amount = 5000
  end_amount = 5005
  invoice_ids = [f"20{num}!@44F" for num in range(first_invoice, last_invoice)]
  comments = [f"Comment {idx}" for idx in range(first_invoice, last_invoice)]
  response = {"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST}
  for idx in range(len(invoice_ids)-1):
    amount = randint(start_amount, end_amount)
    data = {"invoiceId": invoice_ids[idx], "amount": amount, "comments": comments[idx]}
    r = requests.post(url, json=data, headers=headers)
    assert r.json() == response


def test_change_amount_negative_value():
  invoice_id = "2102F"
  amount = -500
  comments = "Comment 1"
  data = {"invoiceId": invoice_id, "amount": amount, "comments": comments}
  status_response = HTTPStatus.OK
  r = requests.post(url, json=data, headers=headers)
  assert r.json()["Code"] != status_response
