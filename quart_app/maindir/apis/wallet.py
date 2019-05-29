import asyncio
import logging
import json
import secrets
from quart import Blueprint, request, jsonify
from quart_openapi import Resource

from ..indyutils.tenant import Tenant
from ..indyutils.wallet.wallet import Wallet
from ..websocket.client import WebsocketClient
from ..indyutils.connections import Connection
from indy.error import IndyError, ErrorCode

walletapi = Blueprint("walletapi", __name__, url_prefix="/wallet")
log = logging.getLogger("indydev")


@walletapi.route("/createwallet", ["POST"])
async def createwallet():
    if request.method == "POST":
        data = json.loads((await request.data))

        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            await asyncio.ensure_future(
                Tenant(
                    wallet_config=wallet_config, wallet_credentials=wallet_creds
                ).create_wallet(name=data["name"])
            )

            return "wallet created"
        except IndyError as e:
            if e.error_code == ErrorCode.WalletAlreadyExistsError:
                return "Wallet Already Exist!"
            else:
                log.exception("wallet creation failed")
                return "wallet creation failed"
        except Exception:
            log.exception("wallet creation failed")
            return "wallet creation failed"

@walletapi.route("/dCard", ["POST"])
async def generate_dCard():
    if request.method == "POST":
        data = json.loads((await request.data))

        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            return await asyncio.ensure_future(
                Tenant(
                    wallet_config=wallet_config, wallet_credentials=wallet_creds
                ).generate_dCard("Bob1")
            )

        except Exception:
            log.exception("Cannot generate dCard")
            return "Cannot generate dCard"


@walletapi.route("/StoreUserDID", ["POST"])
async def storeDID():
    if request.method == "POST":
        data = json.loads((await request.data))

        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            await asyncio.ensure_future(
                Wallet(
                    wallet_config=wallet_config, wallet_credentials=wallet_creds
                ).store_did_and_create_pairwise(
                    data["destinationDID"], data["destinationName"]
                )
            )

            return data["destinationName"] + " created!"
        except Exception:
            log.exception("DID not created!")
            return data["destinationName"] + " not created!"


@walletapi.route("/listDIDs", ["POST"])
async def listDIDs():
    if request.method == "POST":
        data = json.loads((await request.data))
        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            return await Tenant(wallet_config, wallet_creds).listDIDs()

        except Exception:
            log.exception("Could not list destination")
            return "Could not list destination"


@walletapi.route("/listPairwiseDIDs", ["POST"])
async def listPairwiseDIDs():
    if request.method == "POST":
        data = json.loads((await request.data))
        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            return await Tenant(wallet_config, wallet_creds).listPairwiseDIDs()

        except Exception:
            log.exception("Could not list destination")
            return "Could not list destination"


@walletapi.route("/PairwiseInfo", ["POST"])
async def PairwiseInfo():
    if request.method == "POST":
        data = json.loads((await request.data))
        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            return await Tenant(wallet_config, wallet_creds).getPairwiseInfo(
                data["theirDID"]
            )

        except Exception:
            log.exception("Could not list destination")
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
        log.exception("Agent connection failed!")
        return "Agent connection failed!"


@walletapi.route("/records", methods=["GET"])
async def get_wallet_records():
    data = json.loads((await request.data))
    wallet_config = json.dumps({"id": data["walletId"]})
    wallet_creds = json.dumps({"key": data["walletKey"]})
    record_type = data["recordType"]

    if request.method == "GET":
        return await Tenant(wallet_config, wallet_creds).get_wallet_records(
            record_type, "{}"
        )
