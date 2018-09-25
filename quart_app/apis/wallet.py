import asyncio
from quart import Blueprint, logging, json, request
from quart_openapi import Resource
from quart_app.indyutils.wallet import Wallet
walletapi = Blueprint('walletapi', __name__, url_prefix='/wallet')

@walletapi.route('/ho')
async def get():
  '''Hello World Route

  This docstring will show up as the description and short-description
  for the openapi docs for this route.
  '''
  return "hello"

@walletapi.route('/create')
async def createwallet():
    try:
        wallet = Wallet()
        wallet_config = json.dumps({"id": request.args.get("walletId")})
        wallet_creds = json.dumps({"key": request.args.get("walletKey")})
        asyncio.ensure_future(wallet.create_wallet(wallet_config, wallet_creds, "000000000000000000000000Steward1"))

        return "wallet create"
    except:
        return "wallet creation failed"