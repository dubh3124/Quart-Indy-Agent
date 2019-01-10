import logging
import json
from quart import websocket, Blueprint, current_app as app
from ..indyutils.wallet import Wallet
from ..indyutils.connections import Connection
from indy import did

websoc = Blueprint("websoc", __name__)


@websoc.websocket("/connectionrequest")
async def ws():
    while True:
        payload = await websocket.receive()
        logging.info("You've Received a Connection Request!!!")
        data = json.loads(payload)

        try:
            wallet_config = app.config["AGENTID"]
            wallet_creds = app.config["AGENTKEY"]
            # storeDID simulates the storing sender's did on pool ledger. It will not be used.
            # await Wallet(wallet_config, wallet_creds).storeDID(data['did'],data['verkey'], data['name'])

            resp_vk = await Connection().validatesender(data["did"])
            if resp_vk == False:
                await websocket.send("DID not validated")
                raise ConnectionError("Could not validate requestor")
            else:
                response_didkey, response_verkey = await Wallet(
                    wallet_config, wallet_creds
                ).create_pairwise_DID(destinationName="MAIN_George_Billy_DID")
                connection_response = json.dumps(
                    {
                        "did": response_didkey,
                        "verkey": response_verkey,
                        "nonce": data["nonce"],
                    }
                )
                resp = await Connection().anon_encrypt_response(
                    resp_vk, connection_response
                )
                await websocket.send(resp)
        except Exception:
            logging.exception("Error with connection request")
            await websocket.send("DID NOT STORED ABORT")
            raise
