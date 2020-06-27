import json
import pytest
import app
import requests

@pytest.fixture()

def test_lambda_handler(apigw_auth_event):
    print("starting the test. Calling the API link")
    x = requests.get('https://1wwj0frdba.execute-api.us-east-1.amazonaws.com/')
    print('done calling recieved: ' + x.text)
    #ret = app.lambda_handler(apigw_auth_event, "")
    assert ret ==  x.text
