import json
import logging
from indy import did, pairwise, IndyError, non_secrets

from ..indyutils.utils import open_close_wallet
from ..indyutils.indyprotocol.connection import Connection
from ..indyutils.wallet.wallet import Wallet

log = logging.getLogger(__name__)
class Tenant(Wallet):
    @open_close_wallet
    async def listDIDs(self, wallet_handle=None):
        didlist = await did.list_my_dids_with_meta(wallet_handle)
        return didlist

    @open_close_wallet
    async def listPairwiseDIDs(self, wallet_handle=None):
        didlist = await pairwise.list_pairwise(wallet_handle)
        return didlist

    @open_close_wallet
    async def getPairwiseInfo(self, their_did, wallet_handle=None):
        return await pairwise.get_pairwise(wallet_handle, their_did)

    # @open_close_wallet
    # async def store_did_and_create_pairwise(self, didkey, name, wallet_handle=None):
    #     from ..connections import Connection
    #
    #     try:
    #         verkey = await Connection().validatesender(didkey)
    #
    #         await self.storeDID(wallet_handle, didkey, verkey, name)
    #
    #         pairwise_info = json.loads(
    #             (await self.create_pairwise_DID(wallet_handle, didkey, name))
    #         )
    #         pairwise_metadata = json.loads(pairwise_info["metadata"])
    #
    #         await Connection().submitToPool(
    #             pairwise_metadata["pairwiseDID"], pairwise_metadata["pairwiseVerkey"]
    #         )
    #
    #     except IndyError:
    #         log.exception("Error occured while storing DID")
    #         raise
    #     except Exception:
    #         log.exception("Error occured while storing DID")
    #         raise

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

    @open_close_wallet
    async def get_wallet_records(self, record_type, query_json, wallet_handle=None):
        options_json = {
            "retrieveRecords": True,
            "retrieveTotalCount": True,
            "retrieveType": True,
            "retrieveValue": True,
            "retrieveTags": True,
        }
        search_handle = await non_secrets.open_wallet_search(
            wallet_handle, record_type, query_json, json.dumps(options_json)
        )
        return await non_secrets.fetch_wallet_search_next_records(
            wallet_handle, search_handle, count=10
        )

    @open_close_wallet
    async def generate_dCard(self, name, wallet_handle=None):
        invite = await Connection().generate_dCard(name, wallet_handle)
        return invite.as_json()

