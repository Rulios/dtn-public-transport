import requests
import json
from time import sleep


SOURCE_NODE = "dtn://node-2/"
REST_API_URL = "http://127.0.0.1:8081/rest"


def register():
    data = {"endpoint_id": SOURCE_NODE}
    url = REST_API_URL + "/register"  # dtn local server binded to
    try:

        res = requests.post(url, json=data)
        print("Agent registered to node")
        return json.loads(res.text)["uuid"]

    except:
        print("error")


def unregister(uuid):
    data = {"uuid": uuid}
    url = REST_API_URL + "/unregister"  # dtn local server binded to
    try:

        res = requests.post(url, json=data)
        print("agent unregistered from node")

    except Exception as e:
        print("Error unregistering agent from node")
        print(e)


def fetch(uuid):
    data = {"uuid": uuid}
    url = REST_API_URL + "/fetch"  # dtn local server binded to
    try:

        res = requests.post(url, json=data)
        return json.loads(res.text)["bundles"]

    except Exception as e:
        print("Error fetching bundles from node")
        print(e)


try:

    uuid = register()

    # createPackage(
    #     uuid=uuid,
    #     destination="dtn://node-2/",
    #     data="Hello node 2"
    # )

    while True:

        print("Press any key to fetch bundles")

        input()

        print("fetching bundle")
        bundles = fetch(uuid)
        print(bundles)

except KeyboardInterrupt:

    print("Node stopped")
    unregister(uuid)
