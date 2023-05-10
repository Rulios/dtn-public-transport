# from flask import Flask
# import requests
import requests
from time import sleep
import json
import os
import base64


# SOURCE_NODE = "dtn://" + os.environ["NODE_ID"] + "/"
# REST_API_URL = "http://" + os.environ["NODE_LOCAL_IP"] + "/rest"

# please uncommen this 2 lines when deploying
# SOURCE_NODE = os.getenv("NODE_ID", "dtn://node-1/")
# REST_API_URL = os.getenv("NODE_LOCAL_IP" + "/rest",
#                         "http://localhost:8080/rest")


SOURCE_NODE = "dtn://node-2/"
REST_API_URL = "http://localhost:8081/rest"


def buildNodeURL(nodeName):
    return "dtn://" + nodeName + "/"


def register():
    data = {"endpoint_id": SOURCE_NODE}
    url = REST_API_URL + "/register"  # dtn local server binded to
    try:

        res = requests.post(url, json=data)
        print("Agent registered to node")
        return json.loads(res.text)["uuid"]

    except Exception as e:
        print("Failed to register Agent to node")
        print(e)


def unregister(uuid):
    data = {"uuid": uuid}
    url = REST_API_URL + "/unregister"  # dtn local server binded to
    try:

        res = requests.post(url, json=data)
        print("agent unregistered from node")

    except Exception as e:
        print("Error unregistering agent from node")
        print(e)


# iterates through all the payloadBlocks and decodes the base64
# value in the "data" key, returning the original string sent
def returnDataFromPayload(payloadBlocks):
    return [base64.b64decode(block["data"]) for block in payloadBlocks]


def fetch(uuid):
    data = {"uuid": uuid}
    url = REST_API_URL + "/fetch"  # dtn local server binded to

    try:

        res = requests.post(url, json=data)
        return json.loads(res.text)["bundles"]

    except Exception as e:
        print("Error fetching bundles from node")
        print(e)


def createPackage(uuid, destination, dataText):

    print("Bundle information: ")

    data = {
        "uuid": uuid,
        "arguments": {
            "destination": buildNodeURL(destination),
            "source": SOURCE_NODE,
            "creation_timestamp_now": 1,
            "lifetime": "12h",
            "payload_block": dataText
        }
    }

    print(data)
    print("")

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

        print("Press number")
        print("1    - Send bundle")
        print("2    - Fetch bundle")

        option = input()

        print("option: " + option)

        match option:
            case "1":
                print("Enter target node name: ")
                targetNode = input()

                print("Enter message: ")
                message = input()

                print("sending bundle")
                createPackage(
                    uuid=uuid,
                    destination=targetNode,
                    dataText=message
                )

            case "2":

                bundles = fetch(uuid)

                if (len(bundles) > 0):
                    print("Here are the bundles fetched:")
                    canonicalBlocks = bundles[0]["canonicalBlocks"]
                    payloadBlocks = [d for d in canonicalBlocks if d.get(
                        "blockType") == "Payload Block"]

                    print(returnDataFromPayload(payloadBlocks))
                else:
                    print("NO bundles received")
        input()
        os.system("clear")

except KeyboardInterrupt:

    print("Node stopped")
    unregister(uuid)
