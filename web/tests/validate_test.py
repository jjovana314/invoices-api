import pytest
import requests
from json import dumps, loads
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/validate"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


def test_validate_ok():
    data = [
        {
            "debtorCompanyNumber": "10522",
            "creditorCompanyNumber": "12",
            "creditorTaxIdNumber": "13",
            "invoiceNumber": "Racun 20/15",
            "settledAmount": 100,
            "bank": "840"
        },
        {
            "debtorCompanyNumber": "10522",
            "creditorCompanyNumber": "12",
            "creditorTaxIdNumber": "13",
            "invoiceNumber": "Racun 20/11",
            "settledAmount": 20,
            "bank": "840"
        }
    ]
    result = [
        {
            "settlement": {"invoiceId": "2015F"},
            "settlementError": {}
        },
        {
            "settlement": {"invoiceId": "2011F"},
            "settlementError": {}
        }
    ]
    r = requests.post(url=url, json=data, headers=headers)
    assert r.json() == result


def test_validate_schema_invalid():
    data = [
        {
            "debtorCompanyNumber": "10525",
            "creditorCompanyNumber": "12",
            "creditorTaxIdNumber": "13",
            "settledAmount": 1000,
            "bank": "840"
        },
        {
            "debtorCompanyNumber": "10524",
            "creditorCompanyNumber": "12",
            "creditorTaxIdNumber": "13",
            "invoiceNumber": "Racun 18/26",
            "settledAmount": 1002.32,
            "bank": "840"
        }
    ]
    result = {
        "settlement": {},
        "settlementError": {
            "Message": "Schema is not valid",
            "Code": HTTPStatus.BAD_REQUEST
        }
    }
    r = requests.post(url=url, json=data, headers=headers)
    assert r.json() == result
