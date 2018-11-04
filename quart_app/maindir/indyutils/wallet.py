import os
import logging

os.environ["PYTHONASYNCIODEBUG"] = "1"

from quart import json
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError
from .agent import Agent


class Wallet(Agent):
    def __init__(self, wallet_config, wallet_credentials):
        super().__init__()
        self.wallet_config = wallet_config
        self.wallet_credentials = wallet_credentials
        if self.wallet_config == None or self.wallet_credentials == None:
            raise Exception

    async def create_wallet(self, name, seed=None):
        """

        :rtype: str
        """
        try:
            await wallet.create_wallet(self.wallet_config, self.wallet_credentials)
            wallet_handle = await wallet.open_wallet(
                self.wallet_config, self.wallet_credentials
            )
            await self._generate_DID(wallet_handle, seed=seed, name=name)
            await wallet.close_wallet(wallet_handle)
        except IndyError as e:
            logging.exception(e)
            await wallet.delete_wallet(self.wallet_config, self.wallet_credentials)
            raise

    async def create_pairwise_DID(self, seed=None, destinationName=None):
        try:
            wallet_handle = await wallet.open_wallet(
                self.wallet_config, self.wallet_credentials
            )
            didkey, verkey = await self._generate_DID(
                wallet_handle, seed=seed, name=destinationName
            )
            await wallet.close_wallet(wallet_handle)
            return didkey, verkey
        except:
            logging.exception("Oops!")
            raise

    async def listDIDs(self):
        wallet_handle = await wallet.open_wallet(
            self.wallet_config, self.wallet_credentials
        )
        didlist = await did.list_my_dids_with_meta(wallet_handle)
        await wallet.close_wallet(wallet_handle)
        return didlist

    async def storeDID(self, didkey, verkey, name):
        try:
            idjson = json.dumps({"did": didkey, "verkey": verkey})
            metadata = json.dumps({"Name": name})
            wallet_handle = await wallet.open_wallet(
                self.wallet_config, self.wallet_credentials
            )
            await did.store_their_did(wallet_handle, idjson)
            await did.set_did_metadata(wallet_handle, didkey, metadata)
            pool_handle = await pool.open_pool_ledger(config_name=self.pool_name, config=None)
            verkey = await did.key_for_did(pool_handle, wallet_handle, didkey)
            await pool.close_pool_ledger(pool_handle)
            await wallet.close_wallet(wallet_handle)
            return verkey
        except:
            raise

    async def verkeyfromdid(self, didkey):
        try:
            wallet_handle = await wallet.open_wallet(
                self.wallet_config, self.wallet_credentials
            )
            pool_handle = await pool.open_pool_ledger(config_name=self.pool_name, config=None)
            verkey = await did.key_for_did(pool_handle, wallet_handle, didkey)
            await wallet.close_wallet(wallet_handle)
            return verkey
        except:
            raise

    async def didfromseed(self, seed):
        try:
            wallet_handle = await wallet.open_wallet(
                self.wallet_config, self.wallet_credentials
            )
            didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
            await wallet.close_wallet(wallet_handle)
            for didobject in didlist:
                if "metadata" in didobject:
                    meta = json.loads(didobject["metadata"])
                    if isinstance(meta, dict) and meta.get("seed", None) == seed:
                        return didobject.get("did")
        except Exception:
            raise Exception

    async def didfromname(self, name):
        try:
            wallet_handle = await wallet.open_wallet(
                self.wallet_config, self.wallet_credentials
            )
            didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
            print(didlist)
            await wallet.close_wallet(wallet_handle)
            for didobject in didlist:
                if "metadata" in didobject:
                    meta = json.loads(didobject["metadata"])
                    if isinstance(meta, dict) and meta.get("Name", None) == name:
                        return didobject.get("did")
        except Exception:
            raise Exception

    async def _generate_DID(self, wallet_handle, seed=None, name=None):
        seedjson = json.dumps({"seed": seed})
        metadata = json.dumps({"seed": seed, "Name": name})
        didkey, verkey = await did.create_and_store_my_did(wallet_handle, seedjson)
        await did.set_did_metadata(wallet_handle, didkey, metadata)
        return didkey, verkey
