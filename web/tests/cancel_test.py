import pytest
import requests
from json import dumps, loads
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/cancel"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


def test_cancel_invoice_ok():
    invoice_id = "1932F"
    comment = "Invoice not valid"
    data = {"InvoiceId": invoice_id, "CancelComments": comment}
    response = {"Message": "Invoice canceled successfully", "Code": HTTPStatus.OK}
    r = requests.post(url, json=data, headers=headers)
    assert r.json() == response


def test_cancel_invoice_schema_invalid():
    comment = "Invoice not valid"
    data = {"CancelComments": comment}
    response = {"Message": "Schema is not valid", "Code": HTTPStatus.BAD_REQUEST}
    r = requests.post(url, json=data, headers=headers)
    assert r.json() == response


def test_cancel_invoice_schema_invalid():
    invoice_id = "1932F"
    data = {"InvoiceId": invoice_id}
    response = {"Message": "Schema is not valid", "Code": HTTPStatus.BAD_REQUEST}
    r = requests.post(url, json=data, headers=headers)
    assert r.json() == response


def test_cancel_invoice_ok_multiple():
    first_invoice = 11
    last_invoice = 16
    invoice_ids = [f"20{num}F" for num in range(first_invoice, last_invoice)]
    comments = [f"Comment {i}" for i in range(1, 6)]
    response = {"Message": "Invoice canceled successfully", "Code": HTTPStatus.OK}

    for idx in range(len(invoice_ids)-1):
        data = {"InvoiceId": invoice_ids[idx], "CancelComments": comments[idx]}
        r = requests.post(url, json=data, headers=headers)
        assert r.json() == response


def test_cancel_invoice_invalid_schema_multiple():
    comments = [f"Comment {i}" for i in range(1, 6)]
    response = {"Message": "Schema is not valid", "Code": HTTPStatus.BAD_REQUEST}

    for idx in range(len(comments)-1):
        data = {"CancelComments": comments[idx]}
        r = requests.post(url, json=data, headers=headers)
        assert r.json() == response


def test_cancel_invoice_not_exist_multiple():
    first_invoice = 11
    last_invoice = 16
    invoice_ids = [f"20{num}FU$^" for num in range(first_invoice, last_invoice)]
    comments = [f"Comment {i}" for i in range(1, 6)]
    response = {"Message": "Invoice wi", "Code": HTTPStatus.OK}

    for idx in range(len(invoice_ids)-1):
        response = {
            "Message": f"Invoice with id {invoice_ids[idx]} does not exist.",
            "Code": HTTPStatus.BAD_REQUEST
        }
        data = {"InvoiceId": invoice_ids[idx], "CancelComments": comments[idx]}
        r = requests.post(url, json=data, headers=headers)
        assert r.json() == response
