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

import binascii
import time

from pn532pi import Pn532, pn532
from pn532pi import Pn532I2c

#set the communication interface to I2C
PN532_I2C = Pn532I2c(1)
nfc = Pn532(PN532_I2C)


#search for pn532 chipset
def setup():
  print("-------Looking for PN532--------")

  nfc.begin()

  versiondata = nfc.getFirmwareVersion()
  if not versiondata:
    print("Didn't find PN53x board")
    raise RuntimeError("Didn't find PN53x board")  # halt

  # Got ok data, print it out!
  print("Found chip PN5 {:#x} Firmware ver. {:d}.{:d}".format((versiondata >> 24) & 0xFF, (versiondata >> 16) & 0xFF,
                                                             (versiondata >> 8) & 0xFF))

  # configure board to read RFID tags
  nfc.SAMConfig()


DTN_CLIENT_RECHARGE_SERVER_ADDRESS = os.getenv(
    "DTN_CLIENT_RECHARGE_SERVER_ADDRESS", "http://localhost:300'"
)

#performs the operation of writing and reading the data in the card
def loop():

    # Wait for an ISO14443A type card (Mifare, etc.).  When one is found
    # 'uid' will be populated with the UID, and uidLength will indicate
    # if the uid is 4 bytes (Mifare Classic) or 7 bytes (Mifare Ultralight)
    success, uid = nfc.readPassiveTargetID(cardbaudrate=pn532.PN532_MIFARE_ISO14443A_106KBPS)

    if (success):
        # Display some basic information about the card
        print("Found an ISO14443A card")
        print("UID Length: {:d}".format(len(uid)))
        print("UID Value: {}".format(binascii.hexlify(uid)))

        # Make sure this is a Mifare Classic card
        if (len(uid) != 4):
        print("Ooops ... this doesn't seem to be a Mifare Classic card!")
        return

        # We probably have a Mifare Classic card ...
        print("Seems to be a Mifare Classic card (4 byte UID)")


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
    setup()
    app.run(host="0.0.0.0", port=3001, debug=True)
    # app["TEMPLATES_AUTO_RELOAD"] = True
