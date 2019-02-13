import json
import secrets
import logging
from quart import current_app as app
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError
from .agent import Agent
from .wallet import Wallet
from ..websocket.client import WebsocketClient
from .utils import open_close_pool


class Connection(Agent):
    async def establishConnection(self, wallet_id, wallet_credentials, data):
        connection_request = {}
        try:
            pairwise_info = json.loads((await Wallet(
                wallet_id, wallet_credentials
            ).getPairwiseInfo(data["theirDID"])))
            pairwise_metadata = json.loads(pairwise_info["metadata"])
            logging.info(pairwise_metadata)

            connection_request.update(
                {
                    "name": "Agent1_" + data["destinationName"],
                    "did": pairwise_metadata["pairwiseDID"],
                    "nonce": secrets.randbits(32),
                }
            )
            logging.info("Sending to Agent 2")
            resp = await WebsocketClient(
                "ws://192.168.50.181:9002/connectionrequest"
            ).sendMessage(json.dumps(connection_request))
            decrypted_resp = json.loads(
                await Connection().decryptconnectionResponse(
                    wallet_id, wallet_credentials, pairwise_metadata["pairwiseVerkey"], resp
                )
            )
            if connection_request["nonce"] == decrypted_resp["nonce"]:
                await self.submitToPool(
                    decrypted_resp["did"], decrypted_resp["verkey"]
                )
            else:
                raise ValueError(
                    "Connection request and response nonce does not match!"
                )
        except Exception as e:
            logging.exception("Error establishing connection")
            raise e

    @open_close_pool
    async def validatesender(self, didkey, pool_handle=None):
        try:
            wallet_handle = await wallet.open_wallet(self.wallet_id, self.wallet_creds)
            verkey = await did.key_for_did(pool_handle, wallet_handle, didkey)
            await wallet.close_wallet(wallet_handle)
            return verkey
        except IndyError:
            raise

    async def anon_encrypt_response(self, verkey, connection_response):
        resp = await crypto.anon_crypt(verkey, connection_response.encode("utf-8"))
        return resp

    async def sendToAgent(
        self,
        wallet_config,
        wallet_credentials,
        source_did,
        source_verkey,
        connection_request,
    ):
        connection_response = json.dumps(
            {
                "did": source_did,
                "verkey": source_verkey,
                "nonce": connection_request["nonce"],
            }
        )
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        # pool_handle = await pool.open_pool_ledger(config_name=self.pool_name, config=None)

        destination_verkey = await did.key_for_local_did(
            wallet_handle, connection_request["did"]
        )
        anoncrypted_connection_response = await crypto.anon_crypt(
            destination_verkey, connection_response.encode("utf-8")
        )
        return anoncrypted_connection_response

    @open_close_pool
    async def submitToPool(
        self,
        target_did=None,
        target_ver_key=None,
        alias=None,
        pool_handle=None
    ):
        agent_did = await self.get_agent_did()
        agent_wallet_handle = await wallet.open_wallet(self.wallet_id, self.wallet_creds)

        nym_request_json = await self._build_nym_request(
            agent_did, target_did, target_ver_key, alias=alias, role=self.agent_role
        )

        await ledger.sign_and_submit_request(
            pool_handle=pool_handle,
            wallet_handle=agent_wallet_handle,
            submitter_did=agent_did,
            request_json=nym_request_json,
        )
        await wallet.close_wallet(agent_wallet_handle)

    async def decryptconnectionResponse(
        self, wallet_config, wallet_credentials, verkey, encrypted_connection_response
    ):
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        decrypted_resp = (
            await crypto.anon_decrypt(
                wallet_handle, verkey, encrypted_connection_response
            )
        ).decode("utf-8")
        await wallet.close_wallet(wallet_handle)
        # return encrypted_connection_response
        return decrypted_resp

    async def _build_nym_request(
        self, submitter_did, target_did, target_ver_key=None, alias=None, role=None
    ):
        return await ledger.build_nym_request(
            submitter_did, target_did, ver_key=target_ver_key, alias=alias, role=role
        )
