import asyncio
import logging
import json
from quart import Blueprint, request, jsonify
from quart_openapi import Resource
from quart_app.indyutils.wallet import Wallet
from ..websocket.client import WebsocketClient

walletapi = Blueprint('walletapi', __name__, url_prefix='/wallet')


@walletapi.route('/create', ['POST'])
async def createwallet():
    if request.method == 'POST':
        data = (await request.data)
        data = json.loads(data)

        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            wallet = Wallet(wallet_config, wallet_creds)
            await asyncio.ensure_future(
                wallet.create_wallet("000000000000000000000000Steward1"))

            return "wallet created"
        except:
            logging.exception("wallet creation failed")
            return "wallet creation failed"

@walletapi.route('/createDID',['POST'])
async def createDID():
    if request.method == 'POST':
        data = (await request.data)
        data = json.loads(data)

        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            await Wallet(wallet_config, wallet_creds).create_pairwise_DID("000000000000000000000000Steward2", data["destinationName"])
            return data["destinationName"] + " created!"
        except:
            return data["destinationName"] + " not created!"

@walletapi.route('/listDIDs', ['POST'])
async def listDIDs():
    if request.method == 'POST':
        data = (await request.data)
        data = json.loads(data)
        try:
            wallet_config = json.dumps({"id": data["walletId"]})
            wallet_creds = json.dumps({"key": data["walletKey"]})
            return await Wallet(wallet_config, wallet_creds).listDIDs()

        except:
            return "Could not list destination"

@walletapi.route('/send', methods=['POST'])
async def send():
    if request.method == 'POST':
        resp = await WebsocketClient('ws://localhost:5000/connectionrequest').sendMessage((await request.data))
        return resp
