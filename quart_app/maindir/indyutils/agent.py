import asyncio
import json
import logging
import os
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError

from ..indyutils.wallet.agentwallet import AgentWallet
from ..indyutils.utils import open_close_pool


class Agent(AgentWallet):
    log = logging.getLogger("indydev")

    def __init__(self):
        self.genesis_file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "ptgenesis")
        )
        # Set protocol version to 2 to work with the current version of Indy Node
        self.PROTOCOL_VERSION = os.getenv("VERSION")
        self.pool_name = os.environ["POOLNAME"]
        self.wallet_config = json.dumps({"id": os.getenv("AGENTID")})
        self.wallet_credentials = json.dumps({"key": os.getenv("AGENTKEY")})
        self.agent_seed = os.getenv("SEED")
        self.agent_pool_config = os.getenv("POOLCONFIG")
        self.agent_role = "TRUST_ANCHOR"
        self.agent_endpoint = os.getenv("AGENTENDPOINT")

    async def connectToPool(self):
        await self._create_pool_config(
            self.pool_name,
            genesis_file_path=self.genesis_file_path,
            version=self.PROTOCOL_VERSION,
        )

    async def get_agent_did(self):
        return await self.didfromseed(seed=self.agent_seed)

    async def getverkey(self):
        return await self.verkeyfromseed(seed=self.agent_seed)

    async def _create_pool_config(
        self, pool_name, genesis_file_path=None, version=None
    ):
        await pool.set_protocol_version(version)
        # print_log('\n1. Creates a new local pool ledger configuration that is used '
        #           'later when connecting to ledger.\n')
        pool_config = json.dumps({"genesis_txn": genesis_file_path})
        try:
            await pool.create_pool_ledger_config(pool_name, pool_config)
        except IndyError:
            await pool.delete_pool_ledger_config(config_name=pool_name)
            await pool.create_pool_ledger_config(pool_name, pool_config)

    @open_close_pool
    async def submitToPool(
        self,
        target_did=None,
        target_ver_key=None,
        alias=None,
        pool_handle=None,
        wallet_handle=None,
    ):
        agent_did = await self.get_agent_did()

        nym_request_json = await self._build_nym_request(
            agent_did, target_did, target_ver_key, alias=alias, role=self.agent_role
        )

        await ledger.sign_and_submit_request(
            pool_handle=pool_handle,
            wallet_handle=wallet_handle,
            submitter_did=agent_did,
            request_json=nym_request_json,
        )
