import pytest
import requests
from json import dumps, loads
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/paged-liabilities"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


def test_paged_liabilities_multiple_invalid():
    dbt_numbers = [str(num) for num in range(10500, 10550)]
    side = "creditor"
    for dbt_number in dbt_numbers:
        data = {"DebtorCompanyNumber": dbt_number, "Side": side}
        r = requests.post(url=url, json=data, headers=headers)
        data_response = r.json()
        if isinstance(data_response, list):
            for dict_ in data_response:
                assert dict_["Code"] == HTTPStatus.BAD_REQUEST
        if isinstance(data_response, dict):
            for value in data_response.values():
                if isinstance(value, list):
                    for dict_ in value:
                        assert dict_["Code"] == HTTPStatus.BAD_REQUEST
                        assert dict_["Message"] != "Schema is not valid"
                        assert dict_["Message"] != "Side parameter is not valid"

