import requests
import time


def test_decommission_device(mmock_url, workflows_url):
    # start the decommission device workflow
    device_id = "1"
    request_id = "1234567890"
    res = requests.post(
        workflows_url + "/api/v1/workflow/decommission_device",
        json={
            "request_id": request_id,
            "authorization": "Bearer TEST",
            "device_id": device_id,
        },
    )
    assert res.status_code == 201
    # verify the response
    response = res.json()
    assert response is not None
    assert type(response) is dict
    assert response["name"] == "decommission_device"
    assert response["id"] is not None
    # get the job details, every second until done
    for i in range(10):
        time.sleep(1)
        res = requests.get(
            workflows_url + "/api/v1/workflow/decommission_device/" + response["id"]
        )
        assert res.status_code == 200
        # if status is done, break
        response = res.json()
        assert response is not None
        assert type(response) is dict
        if response["status"] == "done":
            break
    # verify the status
    assert {"name": "request_id", "value": request_id} in response["inputParameters"]
    assert {"name": "authorization", "value": "Bearer TEST"} in response[
        "inputParameters"
    ]
    assert {"name": "device_id", "value": device_id} in response["inputParameters"]
    assert response["status"] == "done"
    assert len(response["results"]) == 2
    assert response["results"][0]["success"] == True
    assert response["results"][0]["httpResponse"]["statusCode"] == 204
    #  verify the mock server has been correctly called
    res = requests.get(mmock_url + "/api/request/all")
    assert res.status_code == 200
    response = res.json()
    assert len(response) == 2
    expected = [
        {
            "request": {
                "scheme": "http",
                "host": "mender-inventory",
                "port": "8080",
                "method": "DELETE",
                "path": "/api/0.1.0/devices/" + device_id,
                "queryStringParameters": {},
                "fragment": "",
                "headers": {
                    "Accept-Encoding": ["gzip"],
                    "Authorization": ["Bearer TEST"],
                    "User-Agent": ["Go-http-client/1.1"],
                    "X-Men-Requestid": [request_id],
                },
                "cookies": {},
                "body": "",
            },
        },
        {
            "request": {
                "scheme": "http",
                "host": "mender-deployments",
                "port": "8080",
                "method": "DELETE",
                "path": "/api/management/v1/deployments/deployments/devices/"
                + device_id,
                "queryStringParameters": {},
                "fragment": "",
                "headers": {
                    "Accept-Encoding": ["gzip"],
                    "Authorization": ["Bearer TEST"],
                    "User-Agent": ["Go-http-client/1.1"],
                    "X-Men-Requestid": [request_id],
                },
                "cookies": {},
                "body": "",
            },
        },
    ]
    assert expected[0]["request"] == response[0]["request"]
    assert expected[1]["request"] == response[1]["request"]
