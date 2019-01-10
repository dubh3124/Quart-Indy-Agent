import functools
import asyncio
import logging
import os
from indy import wallet, pool
from indy.error import IndyError




def open_close_wallet(func):
    @functools.wraps(func)
    async def wrapped(*args,**kwargs):
        kwargs["wallet_handle"] = await wallet.open_wallet(args[0].wallet_config, args[0].wallet_credentials)
        try:
            resp = await func(*args,**kwargs)
            await wallet.close_wallet(kwargs["wallet_handle"])
            return resp
        except logging:
            logging.exception("Error while executing function: " + func.__name__)
            await wallet.close_wallet(kwargs["wallet_handle"])
            raise
    return wrapped

def open_close_pool(func):
    @functools.wraps(func)
    async def wrapped(*args,**kwargs):
        logging.info(args)
        kwargs["pool_handle"] = await pool.open_pool_ledger(
            config_name=os.environ["POOLNAME"], config=None
        )
        logging.info(kwargs)
        try:
            resp = await func(*args,**kwargs)
            await pool.close_pool_ledger(kwargs["pool_handle"])
            return resp
        except Exception:
            logging.exception("Error while executing function: " + func.__name__)
            await pool.close_pool_ledger(kwargs["pool_handle"])
            raise
    return wrapped

