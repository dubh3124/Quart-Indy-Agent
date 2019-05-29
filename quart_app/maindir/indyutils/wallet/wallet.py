import os
import logging
import secrets
import asyncio
from quart import json
from indy import pool, ledger, wallet, did, crypto, non_secrets, anoncreds, pairwise
from indy.error import IndyError, ErrorCode

from ...indyutils.wallet.basewallet import BaseWallet
from ..utils import open_close_wallet
from ..indyprotocol.connection import Connection as Connproto

os.environ["PYTHONASYNCIODEBUG"] = "1"
log = logging.getLogger("indydev")


class Wallet(BaseWallet):
    masterSecretIDRecordType = "masterSecretID"

    # def __init__(self, wallet_config=None, wallet_credentials=None):
    #     try:
    #         self.wallet_config = wallet_config
    #         self.wallet_credentials = wallet_credentials
    #         if self.wallet_config is None or self.wallet_credentials is None:
    #             raise Exception
    #     except Exception:
    #         log.exception("no creds")
    #
    # async def create_wallet(self, name, seed=None):
    #     from ..connections import Connection
    #
    #     """
    #
    #     :rtype: str
    #     """
    #     try:
    #         await wallet.create_wallet(self.wallet_config, self.wallet_credentials)
    #         wallet_handle = await wallet.open_wallet(
    #             self.wallet_config, self.wallet_credentials
    #         )
    #         didkey, verkey = await self._generate_DID(
    #             wallet_handle, seed=seed, name=name
    #         )
    #         # await Connection().submitToPool(didkey, verkey)
    #         await Connproto(wallet_handle).generate_dCard(name)
    #         master_secret_id = await self._create_master_secret(wallet_handle)
    #         await self.store_wallet_record(
    #             wallet_handle,
    #             self.masterSecretIDRecordType,
    #             master_secret_id,
    #             record_tags="{}",
    #         )
    #         await wallet.close_wallet(wallet_handle)
    #     except IndyError as e:
    #         log.exception(e)
    #         await wallet.delete_wallet(self.wallet_config, self.wallet_credentials)
    #         raise
    #     except Exception:
    #         log.exception("Error while creating wallet")
    #         await wallet.delete_wallet(self.wallet_config, self.wallet_credentials)
    #         raise

    # async def didfromseed(self, seed, wallet_handle=None):
    #     try:
    #         didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
    #         for didobject in didlist:
    #             if "metadata" in didobject:
    #                 meta = json.loads(didobject["metadata"])
    #                 if isinstance(meta, dict) and meta.get("seed", None) == seed:
    #                     return didobject.get("did")
    #     except IndyError:
    #         raise
    #     except Exception:
    #         raise Exception
    #
    # async def verkeyfromseed(self, seed, wallet_handle=None):
    #     try:
    #         didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
    #         for didobject in didlist:
    #             if "metadata" in didobject:
    #                 meta = json.loads(didobject["metadata"])
    #                 if isinstance(meta, dict) and meta.get("seed", None) == seed:
    #                     return didobject.get("verkey")
    #     except IndyError:
    #         raise Exception
    #     except Exception:
    #         raise Exception
    #
    # #
    # # async def didfromname(self, name, wallet_handle=None):
    # #     try:
    # #         didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
    # #         for didobject in didlist:
    # #             if "metadata" in didobject:
    # #                 meta = json.loads(didobject["metadata"])
    # #                 if isinstance(meta, dict) and meta.get("Name", None) == name:
    # #                     return didobject.get("did")
    # #     except IndyError:
    # #         raise
    # #     except Exception:
    # #         raise Exception
    #
    # async def create_pairwise_DID(
    #     self, wallet_handle, destination_did, destinationName
    # ):
    #     try:
    #         wallet_did = await self.getwalletdid(wallet_handle)
    #         decentid, verkey = await self._generate_DID(wallet_handle)
    #         metadata = {
    #             "Recepient": destinationName,
    #             "pairwiseDID": decentid,
    #             "pairwiseVerkey": verkey,
    #         }
    #         await pairwise.create_pairwise(
    #             wallet_handle,
    #             destination_did,
    #             wallet_did,
    #             metadata=json.dumps(metadata),
    #         )
    #         pairwise_json = await pairwise.get_pairwise(wallet_handle, destination_did)
    #         return pairwise_json
    #     except IndyError:
    #         log.exception("Oops!")
    #         raise
    #     except Exception:
    #         log.exception("Oops!")
    #         raise
    #
    # async def getwalletdid(self, wallet_handle):
    #     try:
    #         didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
    #         for didobject in didlist:
    #             if "metadata" in didobject:
    #                 meta = json.loads(didobject["metadata"])
    #                 if isinstance(meta, dict) and meta["wallet_owner"]:
    #                     return didobject.get("did")
    #     except IndyError:
    #         raise
    #     except Exception:
    #         raise Exception
    #
    # async def getwalletverkey(self, wallet_handle=None):
    #     try:
    #         didlist = json.loads(await did.list_my_dids_with_meta(wallet_handle))
    #         for didobject in didlist:
    #             if "metadata" in didobject:
    #                 meta = json.loads(didobject["metadata"])
    #                 if isinstance(meta, dict) and meta["wallet_owner"]:
    #                     return didobject.get("verkey")
    #     except IndyError:
    #         raise
    #     except Exception:
    #         raise
    #
    # async def get_master_secret_id(self, wallet_handle):
    #     query_json = "{}"
    #     options_json = {
    #         "retrieveRecords": True,
    #         "retrieveTotalCount": True,
    #         "retrieveType": True,
    #         "retrieveValue": True,
    #         "retrieveTags": True,
    #     }
    #     search_handle = await non_secrets.open_wallet_search(
    #         wallet_handle,
    #         self.masterSecretIDRecordType,
    #         query_json,
    #         json.dumps(options_json),
    #     )
    #     query_output = json.loads(
    #         (
    #             await non_secrets.fetch_wallet_search_next_records(
    #                 wallet_handle, search_handle, count=1
    #             )
    #         )
    #     )
    #     log.info(query_output)
    #     master_secret_id = query_output["records"][0]["value"]
    #     return master_secret_id
    #
    # async def _get_wallet_records(self, wallet_handle, record_type, query_json):
    #     options_json = {
    #         "retrieveRecords": True,
    #         "retrieveTotalCount": True,
    #         "retrieveType": True,
    #         "retrieveValue": True,
    #         "retrieveTags": True,
    #     }
    #     search_handle = await non_secrets.open_wallet_search(
    #         wallet_handle, record_type, query_json, json.dumps(options_json)
    #     )
    #     return await non_secrets.fetch_wallet_search_next_records(
    #         wallet_handle, search_handle, count=10
    #     )
    #
    # async def store_wallet_record(
    #     self, wallet_handle, record_type, record_value, record_tags=None
    # ):
    #     record_id = secrets.token_hex(9)
    #     await non_secrets.add_wallet_record(
    #         wallet_handle, record_type, record_id, record_value, tags_json=record_tags
    #     )
    #
    # async def storeDID(self, wallet_handle, didkey, verkey, name):
    #     try:
    #
    #         idjson = json.dumps({"did": didkey, "verkey": verkey})
    #         await did.store_their_did(wallet_handle, idjson)
    #
    #     except IndyError:
    #         log.exception("Error occured while storing DID")
    #         raise
    #     except Exception:
    #         log.exception("Error occured while storing DID")
    #         raise
    #
    # #
    # # async def storeDID(self, didkey, name, verkey="", wallet_handle=None):
    # #     try:
    # #         idjson = json.dumps({"did": didkey})
    # #         metadata = json.dumps({"Name": name})
    # #         await did.store_their_did(wallet_handle, idjson)
    # #         await did.set_did_metadata(wallet_handle, didkey, metadata)
    # #     except IndyError:
    # #         log.exception("Error occured while storing DID")
    # #     except Exception:
    # #         log.exception("Error occured while storing DID")
    #
    # async def _generate_DID(self, wallet_handle, seed=None, name=None):
    #     metadata = json.dumps({"seed": seed, "Name": name, "wallet_owner": True})
    #     didkey, verkey = await did.create_and_store_my_did(wallet_handle, "{}")
    #     await did.set_did_metadata(wallet_handle, didkey, metadata)
    #     return didkey, verkey
    #
    # async def _create_master_secret(self, wallet_handle):
    #     return await anoncreds.prover_create_master_secret(wallet_handle, "")
