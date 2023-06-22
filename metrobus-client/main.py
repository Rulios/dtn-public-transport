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
from flask_sock import Sock
import time

""" from pn532pi import Pn532HSU, Pn532

hsu = Pn532HSU(1)
nfc = Pn532(hsu)


def setup():
    nfc.begin() """
# ...


DTN_CLIENT_RECHARGE_SERVER_ADDRESS = os.getenv(
    "DTN_CLIENT_RECHARGE_SERVER_ADDRESS", "http://localhost:300'"
)


app = Flask(__name__, template_folder=".")
sock = Sock(app)
sock.init_app(app)


availableNodes = []


@app.route("/")
def home():
    return render_template("index.html")


def searchNodeByName(name, nodeSet):
    return [element for element in nodeSet if element["name"] == name] or None


@sock.route("/ws")
def echo(sock):
    while True:
        data = json.loads(sock.receive())

        node = data["value"]

        sock.send(
            json.dumps(
                {
                    "type": "status",
                    "value": "Fetching the recharges in the selected Metro bus",
                }
            )
        )

        ##fetch recharges from node
        nodeAgentServer = searchNodeByName(node, availableNodes)[0]

        recharges = requests.get(nodeAgentServer["agentIP"] + "/get-recharges").json()

        sock.send(
            json.dumps(
                {
                    "type": "status",
                    "value": "Please approach the card into the NFC device...",
                }
            )
        )

        # wait for nfc reader to read

        time.sleep(2)

        sock.send(
            json.dumps(
                {
                    "type": "status",
                    "value": "Updating balance in the card",
                }
            )
        )

        time.sleep(1)

        sock.send(
            json.dumps(
                {
                    "type": "status-complete",
                    "value": "Balance updated, CARD BALANCE: ",
                }
            )
        )

        # download the data into the card

        sock.send(
            json.dumps(
                {
                    "type": "recharges",
                    "value": json.dumps(recharges),
                }
            )
        )

        """ match data.type:
            case "new-selected-node":
                sock.send(
                    json.dumps(
                        {
                            "type": "status",
                            "value": "Please approach the card into the NFC device...",
                        }
                    )
                ) """

        # sock.send(data)


# TO DO, SET UP SERIAL PORT HEARING


@app.route("/get-nodes", methods=["GET"])
def getNodes():
    data = requests.get("http://localhost:3000/get-nodes").json()

    global availableNodes

    availableNodes = data[:]

    return availableNodes


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3001, debug=True)
    # app["TEMPLATES_AUTO_RELOAD"] = True
