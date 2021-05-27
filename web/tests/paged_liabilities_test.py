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
                assert len(list(dict_.values())) > 0

