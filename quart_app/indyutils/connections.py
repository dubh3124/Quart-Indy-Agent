import json
import secrets
import logging
from quart import current_app as app
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError
from .agent import Agent
from .wallet import Wallet
from quart_app.websocket.client import WebsocketClient


class Connection(Agent):
    async def validatesender(self, didkey):
        try:
            wallet_handle = await wallet.open_wallet(
                self.wallet_id, self.wallet_creds
            )
            pool_handle = await pool.open_pool_ledger(config_name=self.pool_name, config=None)

            resp = await did.key_for_did(pool_handle, wallet_handle, didkey)
            await wallet.close_wallet(wallet_handle)
            return resp
        except:
            raise

    async def anon_encrypt_response(self, verkey, connection_response):
        resp = await crypto.anon_crypt(verkey, connection_response.encode("utf-8"))
        return resp

    async def establishConnection(self,
                                  data,
                                  ):
        pairwise_did = await Wallet(self.wallet_id, self.wallet_creds).didfromname(
            data["destinationName"]
        )
        print(pairwise_did)
        verkey = await Wallet(self.wallet_id, self.wallet_creds).verkeyfromdid(pairwise_did)

        connection_request = {
            "name": "MainAgent_" + data["destinationName"],
            "did": pairwise_did,
            "nonce": secrets.randbits(32),
        }
        resp = await WebsocketClient(
            "ws://localhost:5000/connectionrequest"
        ).sendMessage(json.dumps(connection_request))
        decrypted_resp = await Connection().decryptconnectionResponse(
            self.wallet_id, self.wallet_creds, verkey, resp
        )
        return decrypted_resp

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

    async def submitToPool(
        self,
        wallet_config,
        wallet_credentials,
        target_did=None,
        submitter_did=None,
        target_ver_key=None,
        alias=None,
        role=None,
    ):
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        pool_handle = await pool.open_pool_ledger(
            config_name=self.pool_name, config=None
        )

        nym_request_json = await self._build_nym_request(
            submitter_did, target_did, target_ver_key, alias=alias, role=role
        )

        await ledger.sign_and_submit_request(
            pool_handle=pool_handle,
            wallet_handle=wallet_handle,
            submitter_did=submitter_did,
            request_json=nym_request_json,
        )
        await wallet.close_wallet(wallet_handle)
        await pool.close_pool_ledger(pool_handle)

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
