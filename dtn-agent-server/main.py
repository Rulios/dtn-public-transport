from flask import Flask, request
from flask_cors import CORS, cross_origin
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


# once stringified, the data bundles has this structure
# ['{object}', '{object}', ...] NOTE THE QUOTATION MARKS IN THE OBJECTS
# So this function decodes every json string from the array and merges them into a
# central object
def mergeObjects(array):
    central_object = {}

    for item in array:
        try:
            json_data = json.loads(item)
            if isinstance(json_data, dict):
                central_object.update(json_data)
        except json.JSONDecodeError:
            print(f"Failed to decode JSON: {item}")

    return central_object


def fetch(uuid):
    data = {"uuid": uuid}
    url = REST_API_URL + "/fetch"  # dtn local server binded to

    try:
        res = requests.post(url, json=data)
        print(res.text)

        data = json.loads(res.text)["bundles"]

        if len(data) == 0:
            raise Exception("No bundles were fetched")

        return data

    except Exception as e:
        print("Error fetching bundles from node")
        print(e)
        return []


def unpackBundles(bundles):
    # canonicalBlocks = bundles[0]["canonicalBlocks"]
    canonicalBlocks = []

    for bundle in bundles:
        # drop bundles with primaryBlock.bundleControlFlags contains ADMINISTRATIVE_PAYLOAD
        # I theorize that these are bundles related to ping a node

        if "ADMINISTRATIVE_PAYLOAD" not in bundle["primaryBlock"]["bundleControlFlags"]:
            for canonicalBlock in bundle["canonicalBlocks"]:
                canonicalBlocks.append(canonicalBlock)

    payloadBlocks = [
        d for d in canonicalBlocks if d.get("blockType") == "Payload Block"
    ]

    dataInBase64 = returnDataFromPayload(payloadBlocks)

    dataInString = decodeByteToString(dataInBase64)

    return mergeObjects(dataInString)


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

    # print(data)
    print("")

    try:
        res = requests.post(REST_API_URL + "/build", json=data)
        print("bundle sent")
        return True

    except Exception as e:
        print("Error building the package")
        print(e)
        return False


def fetch_with_exponential_backoff(
    fetch_function, *args, max_retries=3, base_delay=1, max_delay=10
):
    retries = 0
    delay = base_delay

    while retries < max_retries:
        try:
            # Invoke the user-provided fetch function with arguments
            data = fetch_function(*args)

            # If the fetch is successful, return the data
            return data

        except Exception as e:
            print(f"Error fetching data: {str(e)}")

            # Increase the number of retries
            retries += 1

            # Calculate the exponential backoff delay
            backoff_delay = random.uniform(0, delay)

            # Increase the delay for the next retry
            delay = min(max_delay, delay * 2)

            print(f"Retrying in {backoff_delay:.2f} seconds...")
            time.sleep(backoff_delay)

    raise Exception(f"Failed to fetch data after {max_retries} retries.")


def announceToMaster():
    nodeMetadata = {
        "node-name": NODE_ID,
        "node-agent-ip": "http://localhost:" + AGENT_PORT,
    }

    # queries the master server and announces the node with the agent
    requests.post(MASTER_CLIENT_URL + "/register-node", json=nodeMetadata)


###############-############-##################-############


# NODE API SERVER TO BE COMMANDED BY MASTER SERVER
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
# bundlesArrived = []  # stors the bundle id that the node has
# recharges = []
recharges = {}  # format {"recharge-id": {target-card, amount, dateTime}, ...}
nodeUuid = register()
print("Announcing to master...")
announceToMaster()
print("Announced to master")


# This route is not by DTN
# This route is when the master server sends the recharges bundle
# to the initial node, so that it can then be propagated
# through DTN
@app.route("/store-recharges-bundle/", methods=["POST"])
def storeRechargesBundle():
    data = request.json

    recharges.update(data["recharges"])

    success = "Stored the initial recharges, ready to be propagated"

    print(success)
    print("Stored this: ")
    print(recharges)
    return success


#   1) Gets the node destination from the master server
#   2) Sends the bundles by DTN that the node has to that
#       destination node
@app.route("/send-to-node", methods=["POST"])
def sendToNode():
    data = request.json

    destination = data["destination"]

    if len(recharges) > 0:
        createPackage(
            uuid=nodeUuid, destination=destination, dataText=json.dumps(recharges)
        )
        print("Sent recharges to " + destination)
    else:
        print("No recharges to send to " + destination)

    print("Recharges length: " + str(len(recharges)))

    return "Ok"


@app.route("/get-recharges", methods=["GET"])
@cross_origin()
def getRechargesInNode():
    return recharges


#   Master server communicates to this node application agent (this server)
#   that it should fetch the bundles arrived.
@app.route("/fetch-bundles", methods=["POST"])
def fetchBundles():
    # retry fetching

    # TO DO, DROP BUNDLES WITH bundleControlFlags=ADMINISTRATIVE_PAYLOAD

    bundlesFetched = fetch_with_exponential_backoff(fetch, nodeUuid)
    # print("bundlesFetched raw ", bundlesFetched)

    fetchedRecharges = unpackBundles(bundlesFetched)
    # print("fetched recharges; ", fetchedRecharges)

    recharges.update(fetchedRecharges)
    print("Received bundles")
    print("Recharges in node: ", str(recharges))

    return "Bundles fetched"


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
