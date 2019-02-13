import functools
import asyncio
import logging
import os
import json
from quart import current_app
from indy import wallet, pool
from indy.error import IndyError

POOL_NAME = os.getenv("POOLNAME")
POOLGENESIS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "ptgenesis")
)


def open_close_wallet(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        kwargs["wallet_handle"] = await wallet.open_wallet(
            args[0].wallet_config, args[0].wallet_credentials
        )
        try:
            if not kwargs["wallet_handle"]:
                raise Exception
            else:
                resp = await func(*args, **kwargs)
                await wallet.close_wallet(kwargs["wallet_handle"])
                return resp
        except Exception:
            logging.exception("Error while executing function: " + func.__name__)
            await wallet.close_wallet(kwargs["wallet_handle"])
            raise

    return wrapped


def open_close_pool(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        # logging.info(POOLGENESIS)
        # await create_pool_config(
        #     POOL_NAME,
        #     genesis_file_path=POOLGENESIS,
        #     version=2,
        # )
        kwargs["pool_handle"] = await pool.open_pool_ledger(
            config_name=os.environ["POOLNAME"], config=None
        )
        logging.info(kwargs)
        try:
            resp = await func(*args, **kwargs)
            await pool.close_pool_ledger(kwargs["pool_handle"])
            # await pool.delete_pool_ledger_config(config_name=POOL_NAME)
            return resp
        except IndyError:
            raise
        except Exception:
            logging.exception("Error while executing function: " + func.__name__)
            await pool.close_pool_ledger(kwargs["pool_handle"])
            # await pool.delete_pool_ledger_config(config_name=POOL_NAME)
            raise

    return wrapped


async def create_pool_config(pool_name, genesis_file_path=None, version=None):
    logging.debug(pool_name)
    logging.debug(genesis_file_path)
    logging.debug(version)
    await pool.set_protocol_version(version)
    # print_log('\n1. Creates a new local pool ledger configuration that is used '
    #           'later when connecting to ledger.\n')
    pool_config = json.dumps({"genesis_txn": genesis_file_path})
    try:

        await pool.create_pool_ledger_config(pool_name, pool_config)

    except IndyError as e:
        logging.exception(e)
        await pool.delete_pool_ledger_config(config_name=pool_name)
        raise
