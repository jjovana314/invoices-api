import pytest
import requests
from http import HTTPStatus

url = "http://127.0.0.1:5000/api/invoice/register"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}


@pytest.mark.skip  # we have already tested this, it will fail because invoice already exists in database
def test_invoice_register_ok():
    invoice_id = "2114F"
    invoice_number = "Racun 21/14"
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


@pytest.mark.skip  # we have already tested this, it will fail because invoice already exists in database
def test_invoice_register_multiple():
    first_invoice = 10
    last_invoice = 15
    invoice_ids = [f"21{num}F" for num in range(first_invoice, last_invoice)]
    invoice_numbers = [f"Racun 21/{num}" for num in range(first_invoice, last_invoice)]
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
        "IDFList": [invoice_ids[idx] for idx in range(len(invoice_ids) - 1)],
        "liability": {"InvoiceNumber": [invoice_numbers[idx] for idx in range(len(invoice_numbers) - 1)]},
        "liabilityError": {
            "InvoiceNumber": [],
            "LimitError": None,
            "SchemaError": None
        }
    }
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


@pytest.mark.skip  # we have already tested this, it will fail because invoice already exists in database
def test_datetime_fail():
    invoice_id = "2116F"
    invoice_number = "Racun 21/16"
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


# @pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_amount_not_ok():
    amount_invalid = "0"
    invoice_number = "Racun 21/17"
    invoice_id = "2117F"
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
            "SchemaError": "Invalid type of data"
        }
    }
    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


@pytest.mark.skip  # we have already tested this, it will fail because invoice already exists in database
def test_dbt_number_register():
    first_invoice = 31
    last_invoice = 36
    invoice_numbers = [f"Racun 21/{num}" for num in range(first_invoice, last_invoice)]
    dbt_numbers = [str(num) for num in range(20500, 20505)]
    amount = 600.52
    for idx_invoice in range(len(invoice_numbers) - 1):
        data = [
            {
                "DebtorCompanyNumber": dbt_numbers[idx_invoice],
                "InvoiceNumber": invoice_numbers[idx_invoice],
                "Amount": amount,
                "IssueDate": "2021-27-05",
                "Comments": f"Comment {idx_invoice + 1}"
            }
        ]
        r = requests.post(url, json=data, headers=headers)
        assert r.status_code == HTTPStatus.OK
        assert r.json()["liability"]["InvoiceNumber"] == [invoice_numbers[idx_invoice]]
