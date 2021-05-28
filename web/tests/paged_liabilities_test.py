import pytest
import requests
from json import dumps, loads
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/paged-liabilities"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


def test_paged_liabilities_multiple_ok():
    dbt_numbers = [str(num) for num in range(20500, 20550)]
    side = "creditor"
    for dbt_number in dbt_numbers:
        data = {"DebtorCompanyNumber": dbt_number, "Side": side}
        r = requests.post(url=url, json=data, headers=headers)
        data_response = r.json()
        if isinstance(data_response, list):
            for dict_ in data_response:
                assert len(dict_.values()) > 0


def test_paged_liabilities_multiple_invalid():
    dbt_numbers = [f"{num}^&" for num in range(1, 10)]
    side = "creditor"
    response = {"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST}
    for dbt_number in dbt_numbers:
        data = {"DebtorCompanyNumber": dbt_number, "Side": side}
        r = requests.post(url=url, json=data, headers=headers)
        assert r.json() == response


def test_paged_liabilities_invalid():
    dbt_number = "1"
    side = "creditor"
    data = {"DebtorCompanyNumber": dbt_number, "Side": side}
    response = {"Message": "Invoice does not exist.", "Code": HTTPStatus.BAD_REQUEST}
    r = requests.post(url=url, json=data, headers=headers)
    assert r.json() == response
