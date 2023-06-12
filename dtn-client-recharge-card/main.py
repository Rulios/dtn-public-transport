from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
import json
from uuid import uuid4


# NODE API SERVER TO BE COMMANDED BY MASTER SERVER
app = Flask(__name__)
CORS(app)

uuid = ""
nodes = []


@app.route("/")
def home():
    return render_template("index.html")


def searchNodeByName(name, nodeSet):
    return [element for element in nodeSet if element["name"] == name] or None


# gets the first node in which the recharge will first be propagated
@app.route("/dispatch-recharges", methods=["POST"])
def dispatchFirstBundle():
    data = request.json

    nodeAgent = searchNodeByName(data["initial-node"], nodes)

    nodeAgentIP = nodeAgent[0]["agentIP"]

    data = {"recharges": data["recharges"]}

    # send
    requests.post(nodeAgentIP + "/store-recharges-bundle", json=data)
    print("Sent initial recharges to initial node")
    return "Ok"


# trigger node-2-node interaction with bundles
@app.route("/dispatch-node-interaction", methods=["POST"])
def dispatchNodeInteraction():
    data = request.json

    collisions = data["collisions"]

    for i in range(len(collisions)):
        collision = collisions[i]

        collider1 = collision[0]["name"]
        collider2 = collision[1]["name"]

        nodeAgentIP1 = searchNodeByName(collider1, nodes)[0]["agentIP"]
        nodeAgentIP2 = searchNodeByName(collider2, nodes)[0]["agentIP"]

        dataToCollider1 = {"destination": collider2}
        dataToCollider2 = {"destination": collider1}

        # exchange bundles between the 2 collider nodes
        requests.post(nodeAgentIP1 + "/send-to-node", json=dataToCollider1)
        requests.post(nodeAgentIP2 + "/send-to-node", json=dataToCollider2)

        print("Exchanged bundles between colliders in collision (%s)", (i))

        # request the collider nodes to fetch the bundles
        requests.post(nodeAgentIP1 + "/fetch-bundles")
        requests.post(nodeAgentIP2 + "/fetch-bundles")

        print("Nodes fetched the exchanged bundles")

    return "Ok"


@app.route("/register-node", methods=["POST"])
def registerNode():
    data = request.json
    nodeName = data["node-name"]
    nodeAgentIP = data["node-agent-ip"]

    if searchNodeByName(nodeName, nodes) == None:
        nodes.append({"name": nodeName, "agentIP": nodeAgentIP})

    print("New node registered (%s - %s)" % (nodeName, nodeAgentIP))
    return "Node Registered"


@cross_origin()
@app.route("/get-nodes", methods=["GET"])
def getNodes():
    return nodes


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
    # app["TEMPLATES_AUTO_RELOAD"] = True
