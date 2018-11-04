import asyncio
import logging
import json
import secrets
from quart import Blueprint, request, jsonify
from quart_openapi import Resource
from ..indyutils.wallet import Wallet
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
            didkey, verkey = await Wallet(
                wallet_config, wallet_creds
            ).create_pairwise_DID(destinationName=data["destinationName"])
            await Wallet(wallet_config, wallet_creds).storeDID(didkey,verkey,data["destinationName"])
            # await Connection().submitToPool(
            #     json.dumps({"id": "Agent"}),
            #     json.dumps({"key": "SuperAgent!"}),
            #     submitter_did= "Th7MpTaRZVRYnPiabds81Y",
            #     target_did=didkey,
            #     target_ver_key=verkey,
            #     alias=None,
            #     role="TRUST_ANCHOR",
            # )
            return data["destinationName"] + " created!"
        except:
            logging.exception("DID not created!")
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
      return await Connection().establishConnection(data)


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
