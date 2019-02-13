import asyncio
import logging
import json
import secrets
from quart import Blueprint, request, jsonify
from quart_openapi import Resource
from ..indyutils.issuance import Issuance
from ..indyutils.wallet import Wallet
from ..websocket.client import WebsocketClient
from ..indyutils.connections import Connection
from ..indyutils.tempjson import cred_offer, cred_req, cred_json


issuanceapi = Blueprint("issuanceapi", __name__, url_prefix="/issuance")


@issuanceapi.route("/schema", ["GET", "POST"])
async def schema():
    if request.method == "POST":
        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        return await Issuance(
            wallet_config=wallet_config, wallet_credentials=wallet_creds
        ).create_credential_schema(
            data["schemaName"], data["schemaVersion"], json.dumps(data["schema"])
        )

    if request.method == "GET":
        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        return await Issuance(
            wallet_config=wallet_config, wallet_credentials=wallet_creds
        ).get_credential_schema(data["schemaID"])


@issuanceapi.route("/definition", ["GET", "POST"])
async def definition():
    if request.method == "POST":
        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        return await Issuance(
            wallet_config=wallet_config, wallet_credentials=wallet_creds
        ).create_credential_definition(data["schemaID"])

    if request.method == "GET":
        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        return await Issuance(
            wallet_config=wallet_config, wallet_credentials=wallet_creds
        ).get_credential_definition(data["credentialDefinitionID"])


@issuanceapi.route("/offer", ["GET", "POST"])
async def offer():
    if request.method == "POST":
        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        return await Issuance(
            wallet_config=wallet_config, wallet_credentials=wallet_creds
        ).create_credential_offer(data["credentialDefinitionID"])


@issuanceapi.route("/request", ["GET", "POST"])
async def cred_request():
    if request.method == "POST":

        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        credential_request_json = await Issuance(
            wallet_config=wallet_config, wallet_credentials=wallet_creds
        ).create_credential_req(data["pairwiseDID"], cred_offer)
        return f"{credential_request_json}"


@issuanceapi.route("/cred", ["GET", "POST"])
async def cred():
    if request.method == "POST":

        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        var1, var2, var3 = await Issuance(
            wallet_config=wallet_config, wallet_credentials=wallet_creds
        ).create_credential(cred_offer, data["cred_req_json"])
        return f"{var1}\n{var2}\n{var3}"


@issuanceapi.route("/storecred", ["GET", "POST"])
async def storeCred():
    try:
        if request.method == "POST":

            data = json.loads((await request.data))
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            await Issuance(
                wallet_config=wallet_config, wallet_credentials=wallet_creds
            ).store_credential_api(data["credentialDefinitionID"], cred_json)

            return "Credential stored!"
    except Exception:
        logging.exception("Credential not stored!")
        return "Credential not stored!"
