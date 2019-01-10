import os
import logging

os.environ["PYTHONASYNCIODEBUG"] = "1"
from quart import json
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError
from .utils import open_close_wallet


class Wallet:
    def __init__(self, wallet_config=None, wallet_credentials=None):
        self.wallet_config = wallet_config
        self.wallet_credentials = wallet_credentials
        if self.wallet_config == None or self.wallet_credentials == None:
            raise Exception

    async def create_wallet(self, name, seed=None):
        from .connections import Connection
        """

        :rtype: str
        """
        try:
            await wallet.create_wallet(self.wallet_config, self.wallet_credentials)
            wallet_handle = await wallet.open_wallet(
                self.wallet_config, self.wallet_credentials
            )
            didkey,verkey = await self._generate_DID(wallet_handle, seed=seed, name=name)
            await Connection().submitToPool(didkey, verkey)
            await wallet.close_wallet(wallet_handle)
        except IndyError as e:
            logging.exception(e)
            await wallet.delete_wallet(self.wallet_config, self.wallet_credentials)
            raise
        except Exception:
            logging.exception("Error while creating wallet")
            await wallet.delete_wallet(self.wallet_config, self.wallet_credentials)
            raise

    @open_close_wallet
    async def create_pairwise_DID(self, wallet_handle=None, seed=None, destinationName=None):
        try:
            didkey, verkey = await self._generate_DID(
                wallet_handle, seed=seed, name=destinationName
            )
            return didkey, verkey
        except:
            logging.exception("Oops!")
            raise

    @open_close_wallet
    async def listDIDs(self,wallet_handle=None):
        didlist = await did.list_my_dids_with_meta(wallet_handle)
        return didlist

    @open_close_wallet
    async def storeDID(self, didkey, verkey, name, wallet_handle=None):
        try:
            idjson = json.dumps({"did": didkey, "verkey": verkey})
            metadata = json.dumps({"Name": name})
            await did.store_their_did(wallet_handle, idjson)
            await did.set_did_metadata(wallet_handle, didkey, metadata)
            return verkey
        except IndyError:
            logging.exception("Error occured while storing DID")
        except Exception:
            logging.exception("Error occured while storing DID")

    @open_close_wallet
    async def getwalletdid(self, wallet_handle=None):
        try:
            didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
            for didobject in didlist:
                if "metadata" in didobject:
                    meta = json.loads(didobject["metadata"])
                    if isinstance(meta, dict) and meta["wallet_owner"] == True:
                        return didobject.get("did")
        except IndyError:
            raise Exception
        except Exception:
            raise Exception

    @open_close_wallet
    async def getwalletverkey(self, wallet_handle=None):
        try:
            didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
            for didobject in didlist:
                if "metadata" in didobject:
                    meta = json.loads(didobject["metadata"])
                    if isinstance(meta, dict) and meta["wallet_owner"] == True:
                        return didobject.get("verkey")
        except IndyError:
            raise
        except Exception:
            raise

    @open_close_wallet
    async def verkeyfromdid(self, didkey, wallet_handle=None):
        try:
            verkey = await did.key_for_local_did(wallet_handle, didkey)
            return verkey
        except IndyError:
            raise
        except Exception:
            raise

    @open_close_wallet
    async def didfromseed(self, seed, wallet_handle=None):
        try:
            didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
            for didobject in didlist:
                if "metadata" in didobject:
                    meta = json.loads(didobject["metadata"])
                    if isinstance(meta, dict) and meta.get("seed", None) == seed:
                        return didobject.get("did")
        except IndyError:
            raise
        except Exception:
            raise Exception

    @open_close_wallet
    async def verkeyfromseed(self, seed, wallet_handle=None):
        try:
            didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
            for didobject in didlist:
                if "metadata" in didobject:
                    meta = json.loads(didobject["metadata"])
                    if isinstance(meta, dict) and meta.get("seed", None) == seed:
                        return didobject.get("verkey")
        except IndyError:
            raise Exception
        except Exception:
            raise Exception

    @open_close_wallet
    async def didfromname(self, name, wallet_handle=None):
        try:
            didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
            for didobject in didlist:
                if "metadata" in didobject:
                    meta = json.loads(didobject["metadata"])
                    if isinstance(meta, dict) and meta.get("Name", None) == name:
                        return didobject.get("did")
        except IndyError:
            raise
        except Exception:
            raise Exception

    async def _generate_DID(self, wallet_handle, seed=None, name=None):
        metadata = json.dumps({"seed": seed, "Name": name, "wallet_owner": True})
        didkey, verkey = await did.create_and_store_my_did(wallet_handle, "{}")
        await did.set_did_metadata(wallet_handle, didkey, metadata)
        return didkey, verkey
