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

issuanceapi = Blueprint("issuanceapi", __name__, url_prefix="/issuance")

@issuanceapi.route("/schema", ["GET","POST"])
async def schema():
    if request.method == "POST":
        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        did = await Wallet(wallet_config, wallet_creds).getwalletdid()
        return await Issuance().create_credntial_schema(wallet_config, wallet_creds, did, data["schemaName"],data["schemaVersion"],json.dumps(data["schema"]))

    if request.method == "GET":
        data = json.loads((await request.data))
        wallet_config = json.dumps({"id": data["walletId"]})
        wallet_creds = json.dumps({"key": data["walletKey"]})
        return await Issuance().get_credential_schema(wallet_config, wallet_creds, data["schemaID"])