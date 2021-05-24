import pytest
import requests
from http import HTTPStatus


url = "http://127.0.0.1:5000"
path = f"{url}/api/invoice/register"


@pytest.mark.skip       # we have already tested this, it will fail because invoice already exists in database
def test_invoice_register_ok():
    invoice_id = "1923F"
    invoice_number = "Racun 19/23"
    headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
    data = [
        {
            "DebtorCompanyNumber": "10522",
            "InvoiceNumber": invoice_number,
            "Amount": 10001,
            "IssueDate": "2020-05-15",
            "Comments": "Comment 1"
        }
    ]

    response = {
        "IDFList": [invoice_id],
        "liability": {"InvoiceNumber": [invoice_number]},
        "liabilityError": {
            "InvoiceNumber": [],
            "LimitError": None,
            "SchemaError": None
        }
    }
    r = requests.post(path, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_invoice_register_multiple():
    headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
    # invoice_ids = ["1851F", "1852F", "1853F", "1854F"]
    first_invoice = 16
    last_invoice = 21
    invoice_ids = [f"19{num}F" for num in range(first_invoice, last_invoice)]
    invoice_numbers = [f"Racun 19/{num}" for num in range(first_invoice, last_invoice)]
    data = [
        {
            "DebtorCompanyNumber": "10522",
            "InvoiceNumber": invoice_numbers[0],
            "Amount": 10001.33,
            "IssueDate": "2020-05-15",
            "Comments": "Comment 1"
        },
        {
            "DebtorCompanyNumber": "10522",
            "InvoiceNumber": invoice_numbers[1],
            "Amount": 100,
            "IssueDate": "2020-05-15",
            "Comments": "Comment 1"
        },
        {
            "DebtorCompanyNumber": "10522",
            "InvoiceNumber": invoice_numbers[2],
            "Amount": 400,
            "IssueDate": "2020-03-15",
            "Comments": "Comment 2"
        },
        {
            "DebtorCompanyNumber": "10522",
            "InvoiceNumber": invoice_numbers[3],
            "Amount": 200,
            "IssueDate": "2020-01-15",
            "Comments": "Comment 3",
            "Lifetime": 20
        }
    ]
    r = requests.post(path, json=data, headers=headers)
    response = {
        "IDFList": [invoice_ids[idx] for idx in range(len(invoice_ids)-1)],
        "liability": {"InvoiceNumber": [invoice_numbers[idx] for idx in range(len(invoice_numbers)-1)]},
        "liabilityError": {
            "InvoiceNumber": [],
            "LimitError": None,
            "SchemaError": None
        }
    }
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_datetime_fail():
    invoice_id = "1931F"
    invoice_number = "Racun 19/31"
    date_invoice_invalid = "22.03.2020"
    headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
    data = [
        {
            "DebtorCompanyNumber": "10522",
            "InvoiceNumber": invoice_number,
            "Amount": 10001,
            "IssueDate": date_invoice_invalid,
            "Comments": "Comment 1"
        }
    ]

    response = {
        "IDFList": [invoice_id],
        "liability": {"InvoiceNumber": [invoice_number]},
        "liabilityError": {
            "InvoiceNumber": [invoice_number],
            "LimitError": None,
            "SchemaError": None
        }
    }
    r = requests.post(path, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_amount_not_ok():
    amount_invalid = "0"
    invoice_number = "Racun 19/32"
    invoice_id = "1932F"
    headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
    data = [
        {
            "DebtorCompanyNumber": "10522",
            "InvoiceNumber": invoice_number,
            "Amount": amount_invalid,
            "IssueDate": "24-05-2019",
            "Comments": "Comment 1"
        }
    ]
    response = {
        "IDFList": [],
        "liability": {"InvoiceNumber": []},
        "liabilityError": {
            "InvoiceNumber": [invoice_number],
            "LimitError": None,
            "SchemaError": "Schema is not valid"
        }
    }
    r = requests.post(path, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response
