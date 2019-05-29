import os
import logging
import secrets
import asyncio
from quart import json
from indy import pool, ledger, wallet, did, crypto, non_secrets, anoncreds, pairwise
from indy.error import IndyError, ErrorCode

from ...indyutils.wallet.basewallet import BaseWallet
from ..utils import open_close_wallet

# from ..indyprotocol.connection import Connection as Connproto

log = logging.getLogger(__name__)


class AgentWallet(BaseWallet):

    async def create_wallet(self, name, seed=None):
        from ...indyutils.connections import Connection

        """

        :rtype: str
        """
        try:
            log.debug(f"Wallet Config: {self.wallet_config} Wallet_Credentials: {self.wallet_credentials}")
            await wallet.create_wallet(self.wallet_config, self.wallet_credentials)
            wallet_handle = await wallet.open_wallet(
                self.wallet_config, self.wallet_credentials
            )
            didkey, verkey = await self._generate_DID(
                wallet_handle, seed=seed, name=name
            )
            await wallet.close_wallet(wallet_handle)
        except IndyError as e:
            if e.error_code == ErrorCode.WalletAlreadyExistsError:
                log.warning("Agent wallet already created!")
            else:
                log.exception(e)
                raise
        except Exception:
            log.exception("Error while creating wallet")
            raise

    # async def listDIDs(self):
    #     didlist = await did.list_my_dids_with_meta(wallet_handle)
    #     return didlist
    #
    # async def listPairwiseDIDs(self, wallet_handle=None):
    #     didlist = await pairwise.list_pairwise(wallet_handle)
    #     return didlist
    #
    # async def getPairwiseInfo(self, their_did, wallet_handle=None):
    #     return await pairwise.get_pairwise(wallet_handle, their_did)
    #
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
    #
    # #
    # # async def verkeyfromdid(self, didkey, wallet_handle=None):
    # #     try:
    # #         verkey = await did.key_for_local_did(wallet_handle, didkey)
    # #         return verkey
    # #     except IndyError:
    # #         raise
    # #     except Exception:
    # #         raise
    #
    #
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
