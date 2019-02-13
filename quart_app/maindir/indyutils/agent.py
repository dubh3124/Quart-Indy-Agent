import asyncio
import json
import logging
import os
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError
from ..indyutils.wallet import Wallet


class Agent(object):
    def __init__(self):
        self.genesis_file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "ptgenesis")
        )
        # Set protocol version to 2 to work with the current version of Indy Node
        self.PROTOCOL_VERSION = os.getenv("VERSION")
        self.pool_name = os.environ["POOLNAME"]
        self.wallet_id = json.dumps({"id": os.getenv("AGENTID")})
        self.wallet_creds = json.dumps({"key": os.getenv("AGENTKEY")})
        self.agent_seed = os.getenv("SEED")
        self.agent_pool_config = os.getenv("POOLCONFIG")
        self.agent_role = "TRUST_ANCHOR"

    async def connectToPool(self):
        await self._create_pool_config(
            self.pool_name,
            genesis_file_path=self.genesis_file_path,
            version=self.PROTOCOL_VERSION,
        )

    async def get_agent_did(self):
        return await Wallet(self.wallet_id, self.wallet_creds).didfromseed(
            seed=self.agent_seed
        )

    async def getverkey(self):
        return await Wallet(self.wallet_id, self.wallet_creds).verkeyfromseed(
            seed=self.agent_seed
        )

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
