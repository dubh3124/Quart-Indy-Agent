import asyncio
import json
from quart import current_app as app
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError

class Agent(object):
    def __init__(self):
        self.genesis_file_path = app.config['POOLGENESIS']
        # Set protocol version to 2 to work with the current version of Indy Node
        self.PROTOCOL_VERSION = app.config['PROTOCOL_VERSION']
        self.pool_name = app.config['POOL_NAME']

    async def connectToPool(self):
        await self._create_pool_config(self.pool_name, genesis_file_path=self.genesis_file_path,
                                                         version=self.PROTOCOL_VERSION)

    async def _create_pool_config(self,pool_name, genesis_file_path=None, version=None):
        await pool.set_protocol_version(version)
        # print_log('\n1. Creates a new local pool ledger configuration that is used '
        #           'later when connecting to ledger.\n')
        pool_config = json.dumps({'genesis_txn': genesis_file_path})
        try:
            await pool.create_pool_ledger_config(pool_name, pool_config)
        except IndyError:
            await pool.delete_pool_ledger_config(config_name=pool_name)
            await pool.create_pool_ledger_config(pool_name, pool_config)
