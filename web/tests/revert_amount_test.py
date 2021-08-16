import pytest
import requests
from json import dumps, loads
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/revert-amount"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


def test_revert_amount_valid():
  data = {"id": 0, "cancelComments": "Comment 1"}
  r = requests.post(url=url, json=data, headers=headers)
  status = HTTPStatus.OK
  assert r.json()["Code"] == status


def test_revert_amount_invalid_schema():
  data = {"cancelComments": "Comments"}
  r = requests.post(url=url, json=data, headers=headers)
  result = {"Message": "Schema is not valid", "Code": HTTPStatus.BAD_REQUEST}
  assert r.json() == result


def test_revert_amount_ok_multiple():
  id_ = 0
  status_response = HTTPStatus.OK
  message = "Amount reverted successfully"
  max_requests_num = 10
  for _ in range(max_requests_num):
    data = {"id": id_, "cancelComments": f"Comment {id_}"}
    r = requests.post(url=url, json=data, headers=headers)
    assert r.json()["Code"] == status_response
    assert r.json()["Message"] == message


def test_revert_amount_schema_invalid_multiple():
  status_response = HTTPStatus.BAD_REQUEST
  message = "Schema is not valid"
  max_requests_num = 10
  for num_requests in range(max_requests_num):
    data = {"cancelComments": f"Comment {num_requests}"}
    r = requests.post(url=url, json=data, headers=headers)
    assert r.json()["Code"] == status_response
    assert r.json()["Message"] == message
