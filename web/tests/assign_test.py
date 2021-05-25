import pytest
import requests
from json import dumps, loads
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/assign"


def test_assign_ok():
    invoice_id = "1903F"
    contract_num = "10534"
    dbt_number = "10524"
    headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
    response = {
        "Code": HTTPStatus.OK,
        "Message": "Invoice assigned successfully"
    }
    data = {'InvoiceId': '1903F', 'AssignmentContractNumber': '10534', 'DebtorCompanyNumber': '10524'}

    r = requests.post(url, json=data, headers=headers)
    assert r.json() == response
