import os
import logging
os.environ['PYTHONASYNCIODEBUG'] = '1'

from quart import json
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError
from .agent import Agent

logging.basicConfig(level=logging.DEBUG)


class Wallet(Agent):
    async def create_wallet(self,wallet_config, wallet_credentials, seed):
        """

        :rtype: str
        """
        # logging.INFO('Creating new secure wallet')
        try:
            pool_handle = await pool.open_pool_ledger(config_name=self.pool_name, config=None)
            logging.DEBUG(pool_handle)
            logging.DEBUG("test")
            #

            # data = json.loads(wallet_config)
            # await wallet.create_wallet(wallet_config, wallet_credentials)
            # wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
            #
            # steward_did, steward_verkey = await self._generate_steward_DID(wallet_handle, seed)
            # await did.set_did_metadata(wallet_handle, steward_did, json.dumps({'seed': seed, 'Name': data['id']}))
            # pool_handle = await pool.open_pool_ledger(config_name="pool1", config=None)
            # logging.INFO(pool_handle + "PULLSHIT")
            # dids = await did.list_my_dids_with_meta(wallet_handle)
            # logging.INFO(dids)
            # #
        except IndyError as e:
            logging.exception(e)
            await wallet.delete_wallet(wallet_config, wallet_credentials)

    async def listDIDs(self, wallet_config, wallet_credentials):
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        dids = await did.list_my_dids_with_meta(wallet_handle)
        print(dids)


    async def _generate_steward_DID(self, wallet_handle, seed):
        # logging.INFO('Generating and storing steward DID and verkey')
        did_json = json.dumps({'seed': seed})
        steward_did, steward_verkey = await did.create_and_store_my_did(wallet_handle, did_json)
        logging.INFO('Steward DID: ', steward_did)
        logging.INFO('Steward Verkey: ', steward_verkey)
        return steward_did, steward_verkey

