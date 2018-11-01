import asyncio
import os
import logging
import json
from quart import Quart
from quart.logging import default_handler
from logging.handlers import RotatingFileHandler
from logging.config import dictConfig
from quart_openapi import Pint
from indy import pool, ledger, wallet, did, crypto
from indy.error import IndyError

from quart_app.indyutils.wallet import Wallet


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
        wallet_handle = await wallet.open_wallet(
            wallet_config, wallet_credentials
        )
        await generate_DID(wallet_handle, seed=seed, name=name)
        await wallet.close_wallet(wallet_handle)
    except IndyError as e:
        logging.exception(e)



async def create_pool_config(
        pool_name, genesis_file_path=None, version=None
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


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    # dictConfig({
    #     'version': 1,
    #     'formatters': {
    #         'verbose': {
    #             'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    #         },
    #         'simple': {
    #             'format': '%(levelname)s %(message)s'
    #         },
    #     },
    #     'handlers': {
    #         'default': {
    #             'level': 'INFO',
    #             'formatter': 'verbose',
    #             'class': 'logging.StreamHandler',
    #         },
    #     },
    #     'loggers': {
    #         'quart.serving': {
    #             'handlers': ['default'],
    #             'level': 'INFO',
    #         },
    #         '__name__': {
    #             'handlers': ['default'],
    #             'level': 'DEBUG',
    #         },
    #         'asyncio': {
    #             'handlers': ['default'],
    #             'level': 'DEBUG',
    #         }
    #     },
    # })

    app = Quart(__name__)

    app.config.from_object("quart_app.config.Config")
    # app.logger.info("Config: %s" % app.config['ENVIRONMENT'])

    # #  Logging
    # import logging
    # logging.basicConfig(
    #     level='DEBUG',
    #     format='%(asctime)s %(levelname)s: %(message)s '
    #            '[in %(pathname)s:%(lineno)d]',
    #     datefmt='%Y%m%d-%H:%M%p',
    # )

    asyncio.get_event_loop().run_until_complete(pool.set_protocol_version(app.config['PROTOCOL_VERSION']))
    asyncio.get_event_loop().run_until_complete(create_pool_config( app.config["POOL_NAME"],genesis_file_path=app.config["POOLGENESIS"], version=app.config["PROTOCOL_VERSION"]))
    asyncio.get_event_loop().run_until_complete(create_wallet(json.dumps({"id": "Agent"}), json.dumps({"key": "SuperAgent!"}),'Agent','000000000000000000000000Steward1'))

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
    from quart_app.apis.wallet import walletapi
    from quart_app.apis.main import main
    from quart_app.websocket.receive import websoc

    app.register_blueprint(main)
    app.register_blueprint(walletapi)
    app.register_blueprint(websoc)
    #
    # # from flask_app.script import resetdb, populatedb
    # # # Click Commands
    # # app.cli
    # # app.cli.add_command(resetdb)
    # # app.cli.add_command(populatedb)
    #



    return app
