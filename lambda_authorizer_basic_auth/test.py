import json
import pytest
import app


@pytest.fixture()
def apigw_auth_event():
    { "key1": "value1", "key2": "value2", "key3": "value3"}

def test_lambda_handler(apigw_auth_event):
    ret = app.lambda_handler(apigw_auth_event, "")
    assert ret == 'Hello World'
