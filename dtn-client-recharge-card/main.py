from flask import Flask, render_template, request
import requests
import json


# NODE API SERVER TO BE COMMANDED BY MASTER SERVER
app = Flask(__name__)


uuid = ""
nodes = []


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dispatch-recharges", methods=["POST"])
def dispatchFirstBundle():
    data = request.json

    print(data["recharges"])
    return "Ok"


@app.route("/register-node", methods=["POST"])
def registerNode():
    data = request.json
    nodeName = data["node-name"]
    nodeAgentIP = data["node-agent-ip"]

    nodes.append({"name": nodeName, "agentIP": nodeAgentIP})
    print("New node registered (%s)" % (nodeName))
    return "Node Registered"


@app.route("/get-nodes", methods=["GET"])
def getNodes():
    return nodes


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
    # app["TEMPLATES_AUTO_RELOAD"] = True
