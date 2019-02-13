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
                Wallet(wallet_config=wallet_config, wallet_credentials=wallet_creds).create_wallet(name=data["name"])
            )

            return "wallet created"
        except:
            logging.exception("wallet creation failed")
            return "wallet creation failed"


@walletapi.route("/StoreUserDID", ["POST"])
async def storeDID():
    if request.method == "POST":
        data = json.loads((await request.data))

        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            await asyncio.ensure_future(
                Wallet(wallet_config=wallet_config, wallet_credentials=wallet_creds).store_did_and_create_pairwise(data["destinationDID"], data["destinationName"])
            )

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

@walletapi.route("/listPairwiseDIDs", ["POST"])
async def listPairwiseDIDs():
    if request.method == "POST":
        data = json.loads((await request.data))
        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            return await Wallet(wallet_config, wallet_creds).listPairwiseDIDs()

        except:
            logging.exception("Could not list destination")
            return "Could not list destination"

@walletapi.route("/PairwiseInfo", ["POST"])
async def PairwiseInfo():
    if request.method == "POST":
        data = json.loads((await request.data))
        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            return await Wallet(wallet_config, wallet_creds).getPairwiseInfo(data["theirDID"])

        except:
            logging.exception("Could not list destination")
            return "Could not list destination"


@walletapi.route("/send", methods=["POST"])
async def send():
    try:
        if request.method == "POST":
            data = json.loads((await request.data))
            wallet_id = json.dumps({"id": data["walletId"]})
            wallet_credentials = json.dumps({"key": data["walletKey"]})
            await Connection().establishConnection(wallet_id, wallet_credentials, data)
            return "connection established"
    except Exception:
        logging.exception("Agent connection failed!")
        return "Agent connection failed!"

@walletapi.route("/records", methods=["GET"])
async def get_wallet_records():
    data = json.loads((await request.data))
    wallet_config = json.dumps({"id": data["walletId"]})
    wallet_creds = json.dumps({"key": data["walletKey"]})
    record_type = data["recordType"]

    if request.method == "GET":
        await Wallet(wallet_config, wallet_creds).get_wallet_records(record_type, """{"value":"Ks8wQ6kdyaVUwT5vxT9wPD:3:CL:26:TestSchema1_def"}""")
        return await Wallet(wallet_config, wallet_creds).get_wallet_records(record_type,"{}")
