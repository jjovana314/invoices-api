import pytest
import requests
from json import dumps, loads
from http import HTTPStatus
from random import randint


url = "http://127.0.0.1:5000/api/invoice/change-amount"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


def test_change_amount_ok():
    invoice_id = "2013F"
    amount = 500
    comments = "Comment 1"
    data = {"invoiceId": invoice_id, "amount": amount, "comments": comments}
    status_response = HTTPStatus.OK
    message = "Amount updated successfully"
    r = requests.post(url, json=data, headers=headers)
    assert r.json()["Message"] == message
    assert r.json()["Code"] == status_response


def test_change_amount_ok_multiple():
    first_invoice = 11
    last_invoice = 16
    start_amount = 5000
    end_amount = 5005
    invoice_ids = [f"20{num}F" for num in range(first_invoice, last_invoice)]
    # todo: u petlji kreirati zahtev i proslediti podatke

