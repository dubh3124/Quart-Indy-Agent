import logging
import json
from indy import crypto, anoncreds, ledger, wallet, pool
from indy.error import IndyError
from .agent import Agent
from .wallet import Wallet



class Issuance(Agent):
    async def create_credntial_schema(self, wallet_id, wallet_credentials, did, schema_name, schema_version, schemajson):
        wallet_handle = await wallet.open_wallet(wallet_id, wallet_credentials)
        pool_handle = await pool.open_pool_ledger(
            config_name=self.pool_name, config=None
        )
        try:
            schema_id, schema = await anoncreds.issuer_create_schema(did,
                                                 schema_name,
                                                 schema_version,
                                                 schemajson)
            schema_request = await self._build_schema_request(did, schema)
            await ledger.sign_and_submit_request(pool_handle, wallet_handle, did, schema_request)
            await pool.close_pool_ledger(pool_handle)
            await wallet.close_wallet(wallet_handle)
            return schema_id
        except IndyError:
            logging.exception("Error occured while creating schema")
            await wallet.close_wallet(wallet_handle)
            await pool.close_pool_ledger(pool_handle)
        except Exception:
            logging.exception("Error occured while creating schema")
            await wallet.close_wallet(wallet_handle)
            await pool.close_pool_ledger(pool_handle)

    async def get_credential_schema(self, wallet_id, wallet_credentials, schema_id):
        pool_handle = await pool.open_pool_ledger(
            config_name=self.pool_name, config=None
        )
        try:
            did = await Wallet(wallet_id,wallet_credentials).getwalletdid()
            get_schema_request = await ledger.build_get_schema_request(did, schema_id)
            get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
            # returns schema_id and schema
            _,schema = await ledger.parse_get_schema_response(get_schema_response)
            return schema
        except IndyError:
            logging.exception("Error occured while creating schema")
            await pool.close_pool_ledger(pool_handle)
        except Exception:
            logging.exception("Error occured while creating schema")
            await pool.close_pool_ledger(pool_handle)

    async def create_credential_definition(self, wallet_id, wallet_credentials,):
        try:
            wallet_handle = await wallet.open_wallet(wallet_id, wallet_credentials)
            pool_handle = await pool.open_pool_ledger(
                config_name=self.pool_name, config=None
            )
            did = await Wallet(wallet_id, wallet_credentials).getwalletdid()
            get_schema_request = await ledger.build_get_schema_request(faber_did, transcript_schema_id)
            get_schema_response = await ledger.submit_request(pool_handle, get_schema_request)
            (transcript_schema_id, transcript_schema) = await ledger.parse_get_schema_response(get_schema_response)
        except IndyError:
            logging.exception("Error while creating credential definition")
            await wallet.close_wallet(wallet_handle)
            await pool.close_pool_ledger(pool_handle)

    async def _build_schema_request(self, did, schema):
       return await ledger.build_schema_request(did, schema)