""" 

Metrobus client server code 

This module act as a standalone client, querying the 
selected node for recharges. This runs on a Le Potato

For research purposes and hardware limitations, this server
queries to the DTN CLIENT RECHARGE server for the available nodes 
directions. 

However, once having that information. To check if a node
has a specific recharge, the server will use that information 
to then query to the INDIVIDUAL NODE AGENT SERVER. 

Once queried, if, there's a recharge, then this server enables
RFID module to write the new recharge status in the tag. 

"""


from flask import Flask, render_template, request
import requests
import json
from uuid import uuid4
import os

DTN_CLIENT_RECHARGE_SERVER_ADDRESS = os.getenv("DTN_CLIENT_RECHARGE_SERVER_ADDRESS")


app = Flask(__name__)


nodes = []


@app.route("/")
def home():
    return render_template("index.html")


def searchNodeByName(name, nodeSet):
    return [element for element in nodeSet if element["name"] == name] or None


def getNodesFromMasterServer():
    data = requests.get(DTN_CLIENT_RECHARGE_SERVER_ADDRESS + "/get-nodes")

    nodes = data


# TO DO, SET UP SERIAL PORT HEARING


@app.route("/get-nodes", methods=["GET"])
def getNodes():
    return nodes


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
    # app["TEMPLATES_AUTO_RELOAD"] = True
