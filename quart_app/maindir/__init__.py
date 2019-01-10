import asyncio
import logging
import json
import sys
import os
from quart import Quart
from indy import pool, wallet, did
from indy.error import IndyError


async def generate_DID(wallet_handle, seed=None, name=None):
    seedjson = json.dumps({"seed": seed})
    metadata = json.dumps({"seed": seed, "Name": name})
    didkey, verkey = await did.create_and_store_my_did(wallet_handle, seedjson)
    await did.set_did_metadata(wallet_handle, didkey, metadata)
    return didkey, verkey


async def create_wallet(wallet_config, wallet_credentials, name, seed=None):
    """

    :rtype: str
    """
    try:
        await wallet.create_wallet(wallet_config, wallet_credentials)
        wallet_handle = await wallet.open_wallet(wallet_config, wallet_credentials)
        await generate_DID(wallet_handle, seed=seed, name=name)
        await wallet.close_wallet(wallet_handle)
    except IndyError as e:
        logging.exception(e)


async def create_pool_config(pool_name, genesis_file_path=None, version=None):
    logging.debug(pool_name)
    logging.debug(genesis_file_path)
    logging.debug(version)
    await pool.set_protocol_version(version)
    # print_log('\n1. Creates a new local pool ledger configuration that is used '
    #           'later when connecting to ledger.\n')
    pool_config = json.dumps({"genesis_txn": genesis_file_path})
    try:

        poolcon = await pool.create_pool_ledger_config(pool_name, pool_config)
        logging.debug(poolcon)
    except IndyError:
        await pool.delete_pool_ledger_config(config_name=pool_name)
        await pool.create_pool_ledger_config(pool_name, pool_config)


def create_app():
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG, handlers=[ch])

    app = Quart(__name__)

    app.config.from_object("maindir.config.Config")
    poolc = asyncio.get_event_loop().run_until_complete(
        create_pool_config(
            app.config["POOL_NAME"],
            genesis_file_path=app.config["POOLGENESIS"],
            version=2,
        )
    )
    logging.debug(poolc)
    asyncio.get_event_loop().run_until_complete(
        create_wallet(
            app.config["AGENTID"], app.config["AGENTKEY"], "Agent", app.config["SEED"]
        )
    )

    # from flask_app.apiv1.auth import jwt
    # jwt.init_app(app)
    #
    # # CORS
    # from flask_cors import CORS
    # CORS(app, supports_credentials=True)
    #
    # # Email
    # from flask_mail import Mail
    # app.mail = Mail(app)
    #
    # # MongoEngine
    # from flask_app.db_init import db
    # app.db = db
    # app.db.init_app(app)
    #
    # Business Logic
    # http://flask.pocoo.org/docs/patterns/packages/
    # http://flask.pocoo.org/docs/blueprints/
    from maindir.apis.wallet import walletapi
    from maindir.apis.issuance import issuanceapi
    from maindir.apis.main import main
    from maindir.websocket.receive import websoc

    app.register_blueprint(main)
    app.register_blueprint(walletapi)
    app.register_blueprint(issuanceapi)
    app.register_blueprint(websoc)
    #
    # # from flask_app.script import resetdb, populatedb
    # # # Click Commands
    # # app.cli
    # # app.cli.add_command(resetdb)
    # # app.cli.add_command(populatedb)
    #

    return app
