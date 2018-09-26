import json
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError


class Connection():
    def __init__(self,pool_name=None):
        self.pool_name = pool_name
    async def sendResponse(self,
                           wallet_config,
                           wallet_credentials,
                           source_did,
                           source_verkey,
                           connection_request):
        connection_response = json.dumps({
            'did': source_did,
            'verkey': source_verkey,
            'nonce': connection_request['nonce']
        })
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        pool_handle = await pool.open_pool_ledger(config_name=self.pool_name, config=None)

        destination_verkey = await did.key_for_did(pool_handle, wallet_handle, connection_request['did'])
        anoncrypted_connection_response = await crypto.anon_crypt(destination_verkey,
                                                                  connection_response.encode('utf-8'))
        return anoncrypted_connection_response


    async def submitRequest(self,
                            wallet_config,
                            wallet_credentials,
                            target_did=None,
                            submitter_did=None,
                            ver_key=None,
                            alias=None,
                            role=None):
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        pool_handle = await pool.open_pool_ledger(config_name=self.pool_name, config=None)

        nym_request_json = await self._build_nym_request(submitter_did, target_did, ver_key=ver_key, alias=alias, role=role)

        await ledger.sign_and_submit_request(pool_handle=pool_handle,
                                             wallet_handle=wallet_handle,
                                             submitter_did=submitter_did,
                                             request_json=nym_request_json)

    async def decryptconnectionResponse(self, wallet_config, wallet_credentials, verkey, encrypted_connection_response):
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        return (await crypto.anon_decrypt(wallet_handle, verkey, encrypted_connection_response)).decode("utf-8")

    async def _build_nym_request(self, submitter_did,
                                 target_did,
                                 ver_key=None,
                                 alias=None,
                                 role=None):
        return await ledger.build_nym_request(submitter_did,
                                       target_did,
                                       ver_key=ver_key,
                                       alias=alias,
                                       role=role)

