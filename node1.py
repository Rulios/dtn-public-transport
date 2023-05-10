# from flask import Flask
# import requests
import requests
from time import sleep
import json
import keyboard

SOURCE_NODE = "dtn://node-1/"
REST_API_URL = "http://127.0.0.1:8080/rest"


def register():
    data = {"endpoint_id": SOURCE_NODE}
    url = REST_API_URL + "/register"  # dtn local server binded to
    try:

        res = requests.post(url, json=data)
        print("Agent registered to node")
        return json.loads(res.text)["uuid"]

    except:
        print("Failed to register Agent to node")


def unregister(uuid):
    data = {"uuid": uuid}
    url = REST_API_URL + "/unregister"  # dtn local server binded to
    try:

        res = requests.post(url, json=data)
        print("agent unregistered from node")

    except Exception as e:
        print("Error unregistering agent from node")
        print(e)


def createPackage(uuid, destination, dataText):
    data = {
        "uuid": uuid,
        "arguments": {
            "destination": destination,
            "source": SOURCE_NODE,
            "creation_timestamp_now": 1,
            "lifetime": "12h",
            "payload_block": dataText
        }
    }

    try:
        res = requests.post(REST_API_URL + "/build", json=data)
        print("bundle sent")
        return True

    except Exception as e:
        print("Error building the package")
        print(e)
        return False


try:

    uuid = register()

    while True:

        print("Press any key to send bundle")

        input()

        print("sending bundle")

        createPackage(
            uuid=uuid,
            destination="dtn://node-2/",
            dataText="Hello node 2"
        )

except KeyboardInterrupt:

    print("Node stopped")
    unregister(uuid)
