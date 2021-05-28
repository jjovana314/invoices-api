import pytest
import requests
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/register"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


@pytest.mark.skip       # we have already tested this, it will fail because invoice already exists in database
def test_invoice_register_ok():
    invoice_id = "1923F"
    invoice_number = "Racun 19/23"
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
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_invoice_register_multiple():
    first_invoice = 11
    last_invoice = 16
    invoice_ids = [f"20{num}F" for num in range(first_invoice, last_invoice)]
    invoice_numbers = [f"Racun 20/{num}" for num in range(first_invoice, last_invoice)]
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
    r = requests.post(url, json=data, headers=headers)
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
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_amount_not_ok():
    amount_invalid = "0"
    invoice_number = "Racun 19/32"
    invoice_id = "1932F"
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
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


def test_dbt_number_register():
    first_invoice = 60
    last_invoice = 65
    invoice_numbers = [f"Racun 21/{num}" for num in range(first_invoice, last_invoice)]
    dbt_numbers = [str(num) for num in range(20500, 20550)]
    amount = 600.52
    for idx_invoice in range(len(invoice_numbers)-1):
        for dbt_number in dbt_numbers:
            data = [
                {
                    "DebtorCompanyNumber": dbt_number,
                    "InvoiceNumber": invoice_numbers[idx_invoice],
                    "Amount": amount,
                    "IssueDate": "2021-27-05",
                    "Comments": f"Comment {idx_invoice+1}"
                }
            ]
            r = requests.post(url, json=data, headers=headers)
            assert r.status_code == HTTPStatus.OK
            assert r.json(),get("Message") != f"Invoice with id {invoice_ids[idx_invoice]} already exist"
            assert r.json().get("liabilityError") == None
