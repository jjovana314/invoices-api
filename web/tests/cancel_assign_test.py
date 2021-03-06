import pytest
import requests
from http import HTTPStatus


url = "http://127.0.0.1:5000/api/invoice/cancel-assign"
headers = {'Content-Type': 'application/json', 'Accept':'application/json'}


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_cancel_assign_ok():
	invoice_id = "2101F"
	data = {"InvoiceId": invoice_id}
	response = {"Message": "Assignation canceled successfully", "Code": HTTPStatus.OK}
	r = requests.post(url, json=data, headers=headers)
	assert r.json() == response


def test_cancel_assign_invalid():
	invoice_id = "000AAAA##"
	data = {"InvoiceId": invoice_id}
	response = {"Message": f"Invoice with id {invoice_id} does not exist.", "Code": HTTPStatus.BAD_REQUEST}
	r = requests.post(url, json=data, headers=headers)
	assert r.json() == response


@pytest.mark.skip   # we have already tested this, it will fail because invoice already exists in database
def test_cancel_assign_multiple_ok():
	idf_num_start = 10
	idf_num_end = 15
	invoice_id_list = [f"21{idf_num}F" for idf_num in range(idf_num_start, idf_num_end)]
	response = {"Message": "Assignation canceled successfully", "Code": HTTPStatus.OK}
	for invoice_id in invoice_id_list:
		data = {"InvoiceId": invoice_id}
		r = requests.post(url, json=data, headers=headers)
		assert r.json() == response


def test_cancel_assign_invalid_multiple():
	idf_num_start = 16
	idf_num_end = 21
	invoice_id_list = [f"19{idf_num}XXXQ@" for idf_num in range(idf_num_start, idf_num_end)]
	for invoice_id in invoice_id_list:
		data = {"InvoiceId": invoice_id}
		r = requests.post(url, json=data, headers=headers)
		assert r.json()["Code"] == HTTPStatus.BAD_REQUEST
