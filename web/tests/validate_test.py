import pytest
import requests
from http import HTTPStatus

url = "http://127.0.0.1:5000/api/invoice/validate"
headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}


@pytest.mark.skip       # we have already tested this, it will fail because invoice already exists in database
def test_validate_ok():
    data_ok = [
        {
            "invoiceNumber": "Racun 21/14",
            "debtorCompanyNumber": "10522",
            "creditorCompanyNumber": "12",
            "creditorTaxIdNumber": "13",
            "settledAmount": 100,
            "bank": "840"
        }
    ]
    result = [
        {
            "settlement": {"invoiceId": "2114F"},
            "settlementError": {}
        }
    ]

    r = requests.post(url=url, json=data_ok, headers=headers)
    assert r.json() == result


# @pytest.mark.skip
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
            "invoiceNumber": "Racun 21/14",
            "settledAmount": 1002.32,
            "bank": "840"
        }
    ]
    settlement_error_result = {
            "Message": "Please enter all required fields",
            "Code": HTTPStatus.BAD_REQUEST
        }
    r = requests.post(url=url, json=data, headers=headers)
    assert r.json()[0].get("settlementError") == settlement_error_result
