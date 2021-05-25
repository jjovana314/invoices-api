import pytest
import requests
from json import dumps, loads
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/assign"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


def test_assign_ok():
    invoice_id = "1903F"
    contract_num = "10534"
    dbt_number = "10524"
    response = {"Code": HTTPStatus.OK, "Message": "Invoice assigned successfully"}
    data = {'InvoiceId': invoice_id, 'AssignmentContractNumber': contract_num, 'DebtorCompanyNumber': dbt_number}

    r = requests.post(url, json=data, headers=headers)
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


def test_assign_invoice_not_exist():
    invoice_id = "AAA00"
    contract_num = "10534"
    dbt_number = "10524"
    data = {'InvoiceId': invoice_id, 'AssignmentContractNumber': contract_num, 'DebtorCompanyNumber': dbt_number}
    r = requests.post(url, json=data, headers=headers)
    response = {"Message": f"Invoice with id {invoice_id} does not exist", "Code": HTTPStatus.BAD_REQUEST}
    assert r.status_code == HTTPStatus.OK
    assert r.json() == response


def test_assign_multiple_invoice():
    first_invoice_num = 11
    last_invoice_num = 16
    invoice_id_list = [f"20{invoice_num}F" for invoice_num in range(first_invoice_num, last_invoice_num)]
    contract_num = "10522"
    dbt_number = "10524"
    for idx_invoice in range(len(invoice_id_list)-1):
        data = {
            "InvoiceId": invoice_id_list[idx_invoice],
            "AssignmentContractNumber": contract_num,
            "DebtorCompanyNumber": dbt_number
        }
        r = requests.post(url, json=data, headers=headers)
        response = {"Code": HTTPStatus.OK, "Message": "Invoice assigned successfully"}
        assert r.status_code == HTTPStatus.OK
        assert r.json() == response


def test_assign_not_valid_multiple_invoice():
    first_invoice_num = 11
    last_invoice_num = 16
    invoice_id_list = [f"20{invoice_num}AAA*$" for invoice_num in range(first_invoice_num, last_invoice_num)]
    contract_num = "10522"
    dbt_number = "10524"
    for idx_invoice in range(len(invoice_id_list)-1):
        data = {
            "InvoiceId": invoice_id_list[idx_invoice],
            "AssignmentContractNumber": contract_num,
            "DebtorCompanyNumber": dbt_number
        }
        r = requests.post(url, json=data, headers=headers)
        response = {
            "Code": HTTPStatus.BAD_REQUEST,
            "Message": f"Invoice with id {invoice_id_list[idx_invoice]} does not exist"
        }
        assert r.status_code == HTTPStatus.OK
        assert r.json() == response
