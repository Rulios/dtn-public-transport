from flask import Flask, request
import requests
from time import sleep
import json
import os
import base64
import uuid
import random

# SOURCE_NODE = "dtn://" + os.environ["NODE_ID"] + "/"
# REST_API_URL = "http://" + os.environ["NODE_LOCAL_IP"] + "/rest"

# please uncommen this 2 lines when deploying
NODE_ID = os.getenv("NODE_ID")
NODE_LOCAL_IP = os.getenv("NODE_LOCAL_IP", "http://localhost:8080")


SOURCE_NODE = "dtn://" + NODE_ID + "/"
REST_API_URL = "http://" + NODE_LOCAL_IP + "/rest"
AGENT_PORT = os.getenv("AGENT_PORT")
MASTER_CLIENT_URL = os.getenv("MASTER_CLIENT_URL")


# SOURCE_NODE = "dtn://node-2/"
# REST_API_URL = "http://localhost:8081/rest"


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
        requests.post(url, json=data)
        print("agent unregistered from node")

    except Exception as e:
        print("Error unregistering agent from node")
        print(e)


# iterates through all the payloadBlocks and decodes the base64
# value in the "data" key, returning the original string sent
def returnDataFromPayload(payloadBlocks):
    return [base64.b64decode(block["data"]) for block in payloadBlocks]


def decodeByteToString(bundles):
    return [data.decode("unicode_escape") for data in bundles]


def fetch(uuid):
    data = {"uuid": uuid}
    url = REST_API_URL + "/fetch"  # dtn local server binded to

    try:
        res = requests.post(url, json=data)
        print(res.text)
        return json.loads(res.text)["bundles"]

    except Exception as e:
        print("Error fetching bundles from node")
        print(e)


def unpackBundles(bundles):
    # canonicalBlocks = bundles[0]["canonicalBlocks"]
    canonicalBlocks = []

    for bundle in bundles:
        for canonicalBlock in bundle["canonicalBlocks"]:
            canonicalBlocks.append(canonicalBlock)

    payloadBlocks = [
        d for d in canonicalBlocks if d.get("blockType") == "Payload Block"
    ]

    dataInBase64 = returnDataFromPayload(payloadBlocks)

    return decodeByteToString(dataInBase64)


def createPackage(uuid, destination, dataText):
    print("Bundle information: ")

    data = {
        "uuid": uuid,
        "arguments": {
            "destination": buildNodeURL(destination),
            "source": SOURCE_NODE,
            "creation_timestamp_now": 1,
            "lifetime": "12h",
            "payload_block": dataText,
        },
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


def retry_with_backoff(retries=5, backoff_in_seconds=1):
    def rwb(f):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return f(*args, **kwargs)
                except:
                    if x == retries:
                        raise

                    sleepTime = backoff_in_seconds * 2**x + random.uniform(0, 1)
                    sleep(sleepTime)
                    x += 1

        return wrapper

    return rwb


def announceToMaster():
    nodeMetadata = {"node-name": NODE_ID, "node-agent-ip": "0.0.0.0:" + AGENT_PORT}

    # queries the master server and announces the node with the agent
    requests.post(MASTER_CLIENT_URL + "/register-node", json=nodeMetadata)


###############-############-##################-############


# NODE API SERVER TO BE COMMANDED BY MASTER SERVER
app = Flask(__name__)

# bundlesArrived = []  # stors the bundle id that the node has
# recharges = []
bundles = {}  # format {"bundle-id": [rechages], ...}
nodeUuid = register()
announceToMaster()


# This route is not by DTN
# This route is when the master server sends the recharges bundle
# to the initial node, so that it can then be propagated
# through DTN
@app.route("/store-recharges-bundle/", methods=["POST"])
def storeRechargesBundle():
    data = request.json

    bundleID = data["bundle-id"]
    recharges = data["recharges"]
    bundles[bundleID] = recharges

    success = "Stored, ready to be propagated"
    print(success)
    return success


#   1) Gets the node destination from the master server
#   2) Sends the bundles by DTN that the node has to that
#       destination node
@app.route("/send-to-node", methods=["POST"])
def sendToNode():
    data = request.json

    destination = data["destination"]

    internalBundleID = uuid.uuid4()
    createPackage(uuid=nodeUuid, destination=destination, dataText=json.dumps(bundles))

    print("Sent bundle " + internalBundleID + " to " + destination)
    return "Sent"


#   Master server communicates to this node application agent (this server)
#   that it should fetch the bundles arrived.
@app.route("/fetch-bundles", methods=["POST"])
def fetchBundles():
    # retry fetching
    @retry_with_backoff(retries=3)
    def fetchWithBackoff():
        bundles = fetch(nodeUuid)

        if len(bundles) == 0:
            raise Exception("Empty fetching, bundle may not have been sent")

        return bundles

    bundlesFetched = fetchWithBackoff()

    bundles.update(bundlesFetched)
    print("Received bundles")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=AGENT_PORT)

""" try:

    uuid = register()

    while True:
        print("This is an app agent for: " + SOURCE_NODE)
        print("Querying REST to URL: " + REST_API_URL)
        print("Press number")
        print("1    - Send bundle")
        print("2    - Fetch bundle")
        print("3    - Send 10 bundles")

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
                    print("Total bundles: " + str(len(bundles)))
                    print(unpackBundles(bundles))
                    # print(type(unpackBundles(bundles)[0]))
                else:
                    print("NO bundles received")

            case "3":
                # send 10 bundles to the target node

                print("Enter target node name: ")
                targetNode = input()

                for i in range(10):
                    print("sending bundle #" + str(i))
                    createPackage(
                        uuid=uuid,
                        destination=targetNode,
                        dataText='bundle #' + str(i)
                    )
                    sleep(1)

                print("ALL BUNDLES SENT, check the other node")
        input()
        os.system("clear")

except KeyboardInterrupt:

    print("Node stopped")
    unregister(uuid)
 """
