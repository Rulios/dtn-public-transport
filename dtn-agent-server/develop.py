from flask import Flask
import requests
from time import sleep
import json
import os
import base64
import atexit


# SOURCE_NODE = "dtn://" + os.environ["NODE_ID"] + "/"
# REST_API_URL = "http://" + os.environ["NODE_LOCAL_IP"] + "/rest"

# please uncommen this 2 lines when deploying
# NODE_ID = os.getenv("NODE_ID", "dtn://node-1/")
# NODE_LOCAL_IP = os.getenv("NODE_LOCAL_IP",
#                           "http://localhost:8080")

# SOURCE_NODE = "dtn://" + NODE_ID + "/"
# REST_API_URL = "http://" + NODE_LOCAL_IP + "/rest"


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

    payloadBlocks = [d for d in canonicalBlocks if d.get(
        "blockType") == "Payload Block"]

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


# try:

#     uuid = register()

#     while True:
#         print("This is an app agent for: " + SOURCE_NODE)
#         print("Press number")
#         print("1    - Send bundle")
#         print("2    - Fetch bundle")
#         print("3    - Send 10 bundles")

#         option = input()

#         print("option: " + option)

#         match option:
#             case "1":
#                 print("Enter target node name: ")
#                 targetNode = input()

#                 print("Enter message: ")
#                 message = input()

#                 print("sending bundle")
#                 createPackage(
#                     uuid=uuid,
#                     destination=targetNode,
#                     dataText=message
#                 )

#             case "2":

#                 bundles = fetch(uuid)

#                 if (len(bundles) > 0):
#                     print("Here are the bundles fetched:")
#                     print("Total bundles: " + str(len(bundles)))
#                     print(unpackBundles(bundles))
#                     # print(type(unpackBundles(bundles)[0]))
#                 else:
#                     print("NO bundles received")

#             case "3":
#                 # send 10 bundles to the target node

#                 print("Enter target node name: ")
#                 targetNode = input()

#                 for i in range(10):
#                     print("sending bundle #" + str(i))
#                     createPackage(
#                         uuid=uuid,
#                         destination=targetNode,
#                         dataText='4Vjl[EDtG2LSkNI283tbnb4rmrOfz5KPGzibd54Vjj3plbiILfbqiIVOEipQY[ko[FYRz4V}ojdF3UIfzP1ThjNiLFHPr1Jq[gCPe33MpXB{5qTk885xFEav4eM[7Y9oBIHMM[1v3ucWOBjHzD4{yT3yd6sCYEEF{KZw8uWj{O[7dOct0JP[ZAJYWsWRVkkHajsVIiSlm7A8wGcuIJrGk[dX5L8hIgmTTekhhJY8DBxwF1,KzjJO9eBzzTFAifaJ' + str(
#                             i)
#                     )
#                     sleep(0.5)

#                 print("ALL BUNDLES SENT, check the other node")
#         input()
#         os.system("clear")

# except KeyboardInterrupt:

#     print("Node stopped")
#     unregister(uuid)


# NODE API SERVER TO BE COMMANDED BY MASTER SERVER
app = Flask(__name__)


uuid = ""


@app.route('/hello/', methods=['GET', 'POST'])
def welcome():
    return "Hello World!"


if __name__ == '__main__':
    uuid = register()
    app.run(host='0.0.0.0', port=5000)
    app.run(debug=True)


# when python terminates, unregister agent from node
atexit.register(unregister(uuid))
