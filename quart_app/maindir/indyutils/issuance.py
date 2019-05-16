import logging
import json
from indy import crypto, anoncreds, ledger, wallet, pool
from indy.error import IndyError
from .wallet.wallet import Wallet
from .utils import open_close_wallet, open_close_pool

log = logging.getLogger("indydev")


class Issuance(Wallet):
    cred_schema_record_type = "credentialSchemas"
    cred_definition_record_type = "credentialDefinitions"
    cred_request_record_type = "credentialRequest"

    @open_close_wallet
    @open_close_pool
    async def create_credential_schema(
        self,
        schema_name,
        schema_version,
        schemajson,
        tags=None,
        wallet_handle=None,
        pool_handle=None,
    ):
        try:
            did = await self.getwalletdid(wallet_handle)
            record_tags = {}
            schema_id, schema = await anoncreds.issuer_create_schema(
                did, schema_name, schema_version, schemajson
            )
            schema_request = await self._build_schema_request(did, schema)
            record_tags["schemaName"] = schema_name
            record_tags["schemaVersion"] = schema_version
            if tags:
                record_tags.update(tags)
            await ledger.sign_and_submit_request(
                pool_handle, wallet_handle, did, schema_request
            )
            await self.store_wallet_record(
                wallet_handle,
                self.cred_schema_record_type,
                schema_id,
                json.dumps(record_tags),
            )
            return schema_id
        except IndyError:
            log.exception("Error occured while creating schema")
            raise
        except Exception:
            log.exception("Error occured while creating schema")
            raise

    @open_close_wallet
    @open_close_pool
    async def get_credential_schema(self, schema_id, wallet_handle, pool_handle=None):
        try:
            did = await self.getwalletdid(wallet_handle)
            get_schema_request = await ledger.build_get_schema_request(did, schema_id)
            get_schema_response = await ledger.submit_request(
                pool_handle, get_schema_request
            )
            # returns schema_id and schema
            _, schema = await ledger.parse_get_schema_response(get_schema_response)
            return schema
        except IndyError:
            log.exception("Error occured while creating schemaa")
            raise
        except Exception:
            log.exception("Error occured while creating schema")
            raise

    @open_close_wallet
    @open_close_pool
    async def create_credential_definition(
        self, schema_id, wallet_handle=None, pool_handle=None
    ):
        try:
            did = await self.getwalletdid(wallet_handle)
            record_tags = {}
            get_schema_request = await ledger.build_get_schema_request(did, schema_id)
            get_schema_response = await ledger.submit_request(
                pool_handle, get_schema_request
            )
            schema_id, schemajson = await ledger.parse_get_schema_response(
                get_schema_response
            )
            schemadict = json.loads(schemajson)
            cred_def_id, cred_def_json = await anoncreds.issuer_create_and_store_credential_def(
                wallet_handle,
                did,
                schemajson,
                tag=schemadict["name"] + "_def",
                signature_type="CL",
                config_json='{"support_revocation": false}',
            )
            record_tags["schemaID"] = schema_id
            record_tags["schemaName"] = schemadict["name"]
            record_tags["schemaVersion"] = schemadict["version"]
            cred_def_request = await ledger.build_cred_def_request(did, cred_def_json)
            resp = await ledger.sign_and_submit_request(
                pool_handle, wallet_handle, did, cred_def_request
            )
            await self.store_wallet_record(
                wallet_handle,
                self.cred_definition_record_type,
                cred_def_id,
                record_tags=json.dumps(record_tags),
            )
            return resp
        except IndyError:
            log.exception("Error while creating credential definition")
            raise
        except Exception:
            log.exception("Error occured while creating definition")
            raise

    @open_close_wallet
    @open_close_pool
    async def get_credential_definition(
        self, cred_def_id, wallet_handle=None, pool_handle=None
    ):
        try:
            did = await self.getwalletdid(wallet_handle)
            get_cred_def_request = await ledger.build_get_cred_def_request(
                did, cred_def_id
            )
            get_cred_def_response = await ledger.submit_request(
                pool_handle, get_cred_def_request
            )
            # returns schema_id and schema
            _, cred_def_json = await ledger.parse_get_cred_def_response(
                get_cred_def_response
            )
            return cred_def_json
        except IndyError:
            log.exception("Error occured while getting credential definition")
            raise
        except Exception:
            log.exception("Error occured while getting credential definition")
            raise

    @open_close_wallet
    async def create_credential_offer(
        self, credential_definition_id, wallet_handle=None
    ):
        try:
            cred_offer_json = await anoncreds.issuer_create_credential_offer(
                wallet_handle, credential_definition_id
            )
            return cred_offer_json
        except IndyError:
            log.exception("Error occured while creating credential offer")
            raise
        except Exception:
            log.exception("Error occured while creating credential offer")
            raise

    @open_close_wallet
    @open_close_pool
    async def create_credential_req(
        self, pairwise_did, cred_offer_json, wallet_handle=None, pool_handle=None
    ):
        try:
            record_tags = {}
            cred_offer = json.loads(cred_offer_json)
            master_secret_id = await self.get_master_secret_id(wallet_handle)
            cred_def_json = await self.get_credential_def(
                cred_offer["cred_def_id"], wallet_handle, pool_handle
            )
            credential_request, credential_request_metadata = await self.create_credential_request(
                wallet_handle,
                pairwise_did,
                json.dumps(cred_offer),
                cred_def_json,
                master_secret_id,
            )
            record_tags["status"] = "pending"
            record_tags["credentialDefinitionID"] = cred_offer["cred_def_id"]
            await self.store_wallet_record(
                wallet_handle,
                self.cred_request_record_type,
                credential_request_metadata,
                record_tags=json.dumps(record_tags),
            )
            return credential_request
        except IndyError:
            log.exception("Error occured while creating credential request")
            raise
        except Exception:
            log.exception("Error occured while creating credential request")
            raise

    # Issuer helpers
    @open_close_wallet
    async def create_credential(
        self, cred_offer_json, cred_request_json, wallet_handle=None
    ):
        cred_values = json.dumps(
            {
                "first_name": {
                    "raw": "Alice",
                    "encoded": "1139481716457488690172217916278103335",
                },
                "last_name": {
                    "raw": "Garcia",
                    "encoded": "5321642780241790123587902456789123452",
                },
                "degree": {
                    "raw": "Bachelor of Science, Marketing",
                    "encoded": "12434523576212321",
                },
                "status": {"raw": "graduated", "encoded": "2213454313412354"},
                "ssn": {"raw": "123-45-6789", "encoded": "3124141231422543541"},
                "year": {"raw": "2015", "encoded": "2015"},
                "average": {"raw": "5", "encoded": "5"},
            }
        )
        cred_json, cred_revoc_id, revoc_reg_delta_json = await anoncreds.issuer_create_credential(
            wallet_handle,
            cred_offer_json,
            json.dumps(cred_request_json),
            cred_values,
            None,
            None,
        )

        return cred_json, cred_revoc_id, revoc_reg_delta_json

    @open_close_wallet
    @open_close_pool
    async def store_credential_api(
        self, cred_def_id, cred_json, wallet_handle=None, pool_handle=None
    ):
        await self.store_credential(wallet_handle, pool_handle, cred_def_id, cred_json)

    async def get_credential_def(self, cred_def_id, wallet_handle, pool_handle):
        try:
            did = await self.getwalletdid(wallet_handle)
            get_cred_def_request = await ledger.build_get_cred_def_request(
                did, cred_def_id
            )
            get_cred_def_response = await ledger.submit_request(
                pool_handle, get_cred_def_request
            )
            # returns schema_id and schema
            _, cred_def_json = await ledger.parse_get_cred_def_response(
                get_cred_def_response
            )
            return cred_def_json
        except IndyError:
            log.exception("Error occured while getting credential definition")
            raise
        except Exception:
            log.exception("Error occured while getting credential definition")
            raise

    # Prover helpers
    async def create_credential_request(
        self,
        wallet_handle,
        pairwise_did,
        cred_offer_json,
        cred_def_json,
        master_secret_id,
    ):

        return await anoncreds.prover_create_credential_req(
            wallet_handle,
            pairwise_did,
            cred_offer_json,
            cred_def_json,
            master_secret_id,
        )

    async def store_credential(
        self, wallet_handle, pool_handle, cred_def_id, cred_json
    ):
        try:
            cred_def_json = await self.get_credential_def(
                cred_def_id, wallet_handle, pool_handle
            )
            cred_def = json.loads(cred_def_json)
            log.info(cred_def)
            query = {"credentialDefinitionID": cred_def["id"]}
            queryresp = json.loads(
                (
                    await self._get_wallet_records(
                        wallet_handle, "credentialRequest", json.dumps(query)
                    )
                )
            )
            cred_request_metadata = queryresp["records"][0]["value"]
            await anoncreds.prover_store_credential(
                wallet_handle,
                None,
                cred_request_metadata,
                cred_json,
                cred_def_json,
                None,
            )
        except IndyError:
            raise
        except Exception:
            raise

    async def _build_schema_request(self, did, schema):
        return await ledger.build_schema_request(did, schema)

    def build_credentials(self, wallet_handle):
        print("hi")
