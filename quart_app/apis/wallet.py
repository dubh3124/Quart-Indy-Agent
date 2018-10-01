import asyncio
import logging
import json
import secrets
from quart import Blueprint, request, jsonify
from quart_openapi import Resource
from quart_app.indyutils.wallet import Wallet
from ..websocket.client import WebsocketClient
from ..indyutils.connections import Connection

walletapi = Blueprint("walletapi", __name__, url_prefix="/wallet")


@walletapi.route("/createwallet", ["POST"])
async def createwallet():
    if request.method == "POST":
        data = json.loads((await request.data))

        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            await asyncio.ensure_future(
                Wallet(wallet_config, wallet_creds).create_wallet(name=data["name"])
            )

            return "wallet created"
        except:
            logging.exception("wallet creation failed")
            return "wallet creation failed"


@walletapi.route("/createDID", ["POST"])
async def createDID():
    if request.method == "POST":
        data = json.loads((await request.data))

        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            await Wallet(wallet_config, wallet_creds).create_pairwise_DID(
                destinationName=data["destinationName"]
            )
            return data["destinationName"] + " created!"
        except:
            return data["destinationName"] + " not created!"


@walletapi.route("/listDIDs", ["POST"])
async def listDIDs():
    if request.method == "POST":
        data = json.loads((await request.data))
        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            return await Wallet(wallet_config, wallet_creds).listDIDs()

        except:
            logging.exception("Could not list destination")
            return "Could not list destination"


@walletapi.route("/send", methods=["POST"])
async def send():
    data = json.loads((await request.data))
    if request.method == "POST":
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        pairwise_did = await Wallet(wallet_config, wallet_creds).didfromname(
            data["destinationName"]
        )
        verkey = await Wallet(wallet_config, wallet_creds).verkeyfromdid(pairwise_did)

        connection_request = {
            "name": "dubh3124_" + data["destinationName"],
            "did": pairwise_did,
            "verkey": verkey,
            "nonce": secrets.randbits(32),
        }
        # return json.dumps(connection_request)
        resp = await WebsocketClient(
            "ws://localhost:5000/connectionrequest"
        ).sendMessage(json.dumps(connection_request))
        decrypted_resp = await Connection().decryptconnectionResponse(
            wallet_config, wallet_creds, verkey, resp
        )
        return decrypted_resp


@walletapi.route("/verkey", methods=["POST"])
async def verkey():
    data = json.loads((await request.data))
    if request.method == "POST":
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        verkey = await Wallet(wallet_config, wallet_creds).verkeyfromdid(
            "3etgvGBSdaNvFrbBMyo5ie"
        )
        return verkey
